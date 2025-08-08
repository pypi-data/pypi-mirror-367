import logging
from datetime import date

import polars as pl
from sqlalchemy import or_

from foundry_sdk.db_mgmt import SQLAlchemyDatabase
from foundry_sdk.db_mgmt.tables import (
    Categories,
    CategoryLevelDescriptions,
    CategoryRelations,
    Companies,
    Datapoints,
    Dates,
    ProductCategories,
    Products,
    Regions,
    SkuTable,
    Stores,
)

# from foundry_sdk.etl.constants import FlagLevels

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading of data into the database using the write_* methods."""

    def __init__(self, db: SQLAlchemyDatabase, insertion_mode: str) -> None:
        """
        Args:
            db (SQLAlchemyDatabase): Database connection object.
            insertion_mode (InsertionMode): Mode for database insertion.

        """
        # db ignored, is legacy, will be removed from arguments in the future
        self.insertion_mode = insertion_mode
        self.db = db  # to be removed in the future

    #################################### Mandatory data ############################################

    @staticmethod
    def check_check_passed(*, check_passed: bool) -> None:
        if not check_passed:
            raise ValueError("wait for all checks to pass")

    def write_company(
        self,
        name: str,
        dataset_type: str,
        description: str,
        min_date: date,
        max_date: date,
        frequency: int,
        *,
        check_passed: bool,
    ) -> int:
        """Writes the company metadata and returns the company ID."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare company data as dictionary
        company_data = {
            "name": name,
            "dataset_type": dataset_type,
            "description": description,
            "min_date": min_date,
            "max_date": max_date,
            "frequency": frequency,
        }

        # Use the modern insertion method with configured mode
        company_id = db.handle_insertion_single_line(
            model_class=Companies,
            data=company_data,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing company '%s' to db complete, got ID %s", name, company_id)
        return company_id

    def write_stores(self, store_region_map: pl.DataFrame, company_id: int, *, check_passed: bool) -> pl.DataFrame:
        """Write store entries to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get unique combinations of region, country, level to look up region IDs
        region_lookup = store_region_map.select(["region", "country", "level"]).unique()

        with db.get_session(read_only=True) as session:
            # Query region IDs from database
            country_abbrevs = region_lookup.select("country").unique().to_series().to_list()
            country_query = (
                session.query(Regions.id, Regions.abbreviation)
                .filter(Regions.abbreviation.in_(country_abbrevs), Regions.type == "country")
                .all()
            )

            country_id_map = {abbrev: region_id for region_id, abbrev in country_query}

            # Build region lookup with country IDs
            region_lookup_with_country_ids = region_lookup.with_columns(
                pl.col("country").replace(country_id_map).alias("country_id").cast(pl.Int64)
            )

            # Query all region IDs in one batch
            region_conditions = [
                (Regions.abbreviation == row["region"])
                & (Regions.type == row["level"])
                & (Regions.country == row["country_id"])
                for row in region_lookup_with_country_ids.to_dicts()
            ]

            region_results = (
                session.query(Regions.id, Regions.abbreviation, Regions.type, Regions.country)
                .filter(or_(*region_conditions))
                .all()
            )

            # Build Polars DataFrame directly from results
            region_id_df = pl.DataFrame(
                [
                    {
                        "region_id": region_id,
                        "region": abbreviation,
                        "level": region_type,
                        "country_id": country_id,
                    }
                    for region_id, abbreviation, region_type, country_id in region_results
                ]
            )

        store_region_map = (
            store_region_map.join(region_lookup_with_country_ids, on=["region", "country", "level"], how="left")
            .join(region_id_df, on=["region", "country_id", "level"], how="left")
            .select(["store", "region_id"])
            .rename({"region_id": "regionID", "store": "name"})
            .with_columns(companyID=pl.lit(company_id))
        )

        # Use bulk insertion method
        result = db.handle_insertion_multi_line(
            model_class=Stores,
            data=store_region_map,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing stores to db complete, got %d store IDs back", len(result))

        return result

    def write_categories(
        self,
        categories_dict: dict,
        categories_level_description: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Writes categories and their relations to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare category level descriptions
        categories_level_description = categories_level_description.with_columns(companyID=pl.lit(company_id)).sort(
            "level"
        )

        # Write category level descriptions
        db.handle_insertion_multi_line(
            model_class=CategoryLevelDescriptions,
            data=categories_level_description,
            mode=self.insertion_mode,
            returning_id=False,
        )
        logger.info("Successfully wrote %d category level descriptions", len(categories_level_description))

        all_categories = []
        all_relations = []

        # Process categories by level
        for row in categories_level_description.to_dicts():
            level = row["level"]
            level_name = row["name"]
            logger.info("Processing level %d: %s", level, level_name)

            relevant_categories = categories_dict[level]

            # Prepare unique categories for this level
            unique_categories = pl.DataFrame(
                {"name": list(relevant_categories.keys()), "companyID": [company_id] * len(relevant_categories)}
            )

            # Write categories for this level
            categories_result = db.handle_insertion_multi_line(
                model_class=Categories,
                data=unique_categories,
                mode=self.insertion_mode,
                returning_id=True,
            )

            all_categories.append(categories_result)

            # Process category relations if there are parent-child relationships
            if relevant_categories:
                relations_data = self._extract_category_relations(relevant_categories)
                if not relations_data.is_empty():
                    # Get category IDs for relations
                    relations_with_ids = self._resolve_category_relation_ids(
                        db, relations_data, company_id, is_top_level=level == categories_level_description[0, "level"]
                    )

                    if not relations_with_ids.is_empty():
                        # Write category relations
                        db.handle_insertion_multi_line(
                            model_class=CategoryRelations,
                            data=relations_with_ids,
                            mode=self.insertion_mode,
                            returning_id=False,
                        )
                        all_relations.append(relations_with_ids)

            logger.info("Successfully wrote level %d categories (%s) into the database", level, level_name)

        # Combine all category results
        if all_categories:
            return pl.concat(all_categories)

        return pl.DataFrame(schema={"name": pl.Utf8, "companyID": pl.Int64, "ID": pl.Int64})

    def _extract_category_relations(self, categories_dict: dict) -> pl.DataFrame:
        """Extract parent-child relationships from categories dictionary."""
        relations = []

        for child_name, parents in categories_dict.items():
            if isinstance(parents, list | tuple | dict):
                parent_names = parents if isinstance(parents, list | tuple) else list(parents.keys())
                for parent_name in parent_names:
                    relations.append({"parentCategory": parent_name, "subCategory": child_name})

        if relations:
            return pl.DataFrame(relations)

        return pl.DataFrame(schema={"parentCategory": pl.Utf8, "subCategory": pl.Utf8})

    def _resolve_category_relation_ids(
        self,
        db: SQLAlchemyDatabase,
        relations_df: pl.DataFrame,
        company_id: int,
        *,
        is_top_level: bool,
    ) -> pl.DataFrame:
        """Resolve category names to IDs for relations."""
        if relations_df.is_empty():
            return pl.DataFrame(schema={"subID": pl.Int64, "parentID": pl.Int64})

        # Get unique category names
        sub_categories = relations_df.select("subCategory").unique().to_series().to_list()
        parent_categories = relations_df.select("parentCategory").unique().to_series().to_list()
        all_category_names = list(set(sub_categories + parent_categories))

        # Query category IDs in batch
        with db.get_session(read_only=True) as session:
            category_results = (
                session.query(Categories.id, Categories.name)
                .filter(Categories.company_id == company_id, Categories.name.in_(all_category_names))
                .all()
            )

        # Build category name to ID mapping
        category_id_map = {name: cat_id for cat_id, name in category_results}

        # Add IDs to relations
        relations_with_ids = relations_df.with_columns(
            [
                pl.col("subCategory").replace(category_id_map).alias("subID").cast(pl.Int64),
                pl.col("parentCategory").replace(category_id_map).alias("parentID").cast(pl.Int64),
            ]
        ).select(["subID", "parentID"])

        # For top level, remove relations where parent ID is null (no parent)
        if is_top_level:
            relations_with_ids = relations_with_ids.drop_nulls()

        return relations_with_ids

    def write_products(self, products: pl.DataFrame, company_id: int, *, check_passed: bool) -> pl.DataFrame:
        """Writes product entries to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        products = (
            products.with_columns(
                companyID=pl.lit(company_id),
            )
            .drop("category")
            .rename({"product": "name"})
        )

        # Use bulk insertion method
        result = db.handle_insertion_multi_line(
            model_class=Products,
            data=products,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing products to db complete, got %d product IDs back", len(result))

        return result

    def write_product_categories(
        self,
        products: pl.DataFrame,
        product_ids: pl.DataFrame,
        category_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Link products to categories and write associations."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Create product-category mapping using polars-native operations
        products = (
            products.join(
                product_ids.rename({"name": "product", "ID": "productID"}),
                on="product",
                how="left",
            )
            .join(
                category_ids.select(["name", "ID"]).rename({"name": "category", "ID": "categoryID"}),
                on="category",
                how="left",
            )
            .select(["productID", "categoryID"])
        )

        # Use bulk insertion method
        db.handle_insertion_multi_line(
            model_class=ProductCategories,
            data=products,
            mode=self.insertion_mode,
            returning_id=False,
        )

        logger.info("Writing product categories to db complete, linked %d product-category pairs", len(products))

        return True

    def write_skus(
        self,
        time_sku_data: pl.DataFrame,
        store_ids: pl.DataFrame,
        product_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Write SKU entries (product-store combinations) to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get unique store-product pairs
        time_sku_data = (
            time_sku_data.select(["store", "product"])
            .unique()
            .join(store_ids.drop("companyID").rename({"name": "store", "ID": "storeID"}), on="store", how="left")
            .join(
                product_ids.drop("companyID").rename({"name": "product", "ID": "productID"}), on="product", how="left"
            )
        )

        time_sku_combinations = time_sku_data.select(["storeID", "productID"])

        # Write to SKU table
        result = db.handle_insertion_multi_line(
            model_class=SkuTable,
            data=time_sku_combinations,
            mode=self.insertion_mode,
            returning_id=True,
        )

        time_sku_data = time_sku_data.join(result.rename({"ID": "skuID"}), on=["storeID", "productID"], how="left")

        logger.info("Writing SKUs to db complete, got %d sku IDs back", len(result))

        return time_sku_data  # this is sku_ids in the next function

    def write_datapoints(
        self,
        time_sku_data: pl.DataFrame,
        sku_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Create and write datapoint entries (sku-time combinations)."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get all dates from the db as polars DataFrame
        with db.get_session(read_only=True) as session:
            date_rows = session.query(Dates.id, Dates.date).all()
        dates_df = pl.DataFrame([{"dateID": row[0], "date": row[1]} for row in date_rows])

        # Merge time_sku_data with sku_ids on product, store
        time_sku_data = (
            time_sku_data.select(["product", "store", "date"])
            .unique()
            .join(sku_ids, on=["product", "store"], how="left")
            .join(dates_df, on="date", how="left")
            .select(["skuID", "dateID"])
        )

        # Write to Datapoints table
        result = db.handle_insertion_multi_line(
            model_class=Datapoints,
            data=time_sku_data,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing datapoints to db complete, got %d datapoint IDs back", len(result))

        result = (
            result.rename({"ID": "datapointID"})
            .join(sku_ids, on=["skuID"], how="left")
            .join(dates_df, on=["dateID"], how="left")
        )

        return result

    def write_time_sku_data(
        self,
        time_sku_feature_description_map: pl.DataFrame,
        time_sku_data: pl.DataFrame,
        datapoint_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """
        Create and write time-sku data entries (features for each datapoint).

        Args:
            time_sku_feature_description_map: Polars DataFrame with feature metadata (must include 'name', 'description', 'var_type').
            time_sku_data_with_datapoint_id: Polars DataFrame with columns ['datapointID', 'feature', 'value'] (and possibly others).
            company_id: The company ID for all features.
            check_passed: Ensure all checks have passed before writing.

        Returns:
            Polars DataFrame of written time-sku features (with featureID, datapointID, value).

        """
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare feature description map
        time_sku_feature_description_map = time_sku_feature_description_map.with_columns(
            companyID=pl.lit(company_id), feature_type=pl.lit("time_sku")
        )

        print(time_sku_feature_description_map)

        assert False

        # # Write feature descriptions
        # feature_description_result = db.handle_insertion_multi_line(
        #     model_class=FeatureDescriptions,
        #     data=time_sku_feature_description_map,
        #     mode=self.insertion_mode,
        #     returning_id=True,
        # )

        # # Add featureID to feature description map
        # feature_desc = feature_desc.with_columns(featureID=pl.Series(feature_description_result["ID"]))
        # feature_desc = feature_desc.rename({"name": "feature"})

        # # Prepare feature map for writing
        # feature_map = time_sku_data_with_datapoint_id.join(
        #     feature_desc.select(["feature", "featureID"]), on="feature", how="left"
        # ).select(["datapointID", "featureID", "value"])

        # # Write time-sku features
        # db.handle_insertion_multi_line(
        #     model_class=TimeSkuFeatures,
        #     data=feature_map,
        #     mode=self.insertion_mode,
        #     returning_id=False,
        # )

        # logger.info("Writing time-sku features to the database complete, wrote %d rows", len(feature_map))

        # return feature_map

    # def prep_levels(self, feature_description, feature_description_map, levels) -> t.Tuple[pd.DataFrame]:
    #     ids = feature_description.ids
    #     feature_id_mapping = feature_description_map[["name"]].copy()
    #     feature_id_mapping.rename(columns={"name": "feature"}, inplace=True)
    #     feature_id_mapping["featureID"] = ids
    #     levels = levels.merge(feature_id_mapping, on="feature", how="left")
    #     levels.rename(columns={"levels": "level"}, inplace=True)
    #     del levels["feature"]

    #     return levels

    # def write_time_sku_data(
    #     self,
    #     time_sku_feature_description_map: pd.DataFrame,
    #     time_sku_data_with_datapoint_id: pd.DataFrame,
    #     company_object: Companies,
    #     create_new_time_sku_table: bool = True,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, t.Any]:
    #     """Create and write time-sku data entries."""

    #     company_id = company_object.ids
    #     time_sku_feature_description_map = clean_and_check_time_sku_feature_description_map(
    #         time_sku_feature_description_map, copy=True
    #     )
    #     time_sku_feature_description_map["companyID"] = company_id
    #     #! remove levels as they should not be used ofr time-sku features

    #     time_sku_feature_description_map, _ = self.extract_levels(time_sku_feature_description_map)

    #     time_sku_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     # time_sku_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     time_sku_feature_description_map["feature_type"] = "time_sku"
    #     time_sku_feature_description.write_to_db_multi_row(time_sku_feature_description_map, save_ids=True)
    #     del time_sku_feature_description_map["feature_type"]

    #     # levels = self.prep_levels(time_sku_feature_description, time_sku_feature_description_map, levels)
    #     # time_sku_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     columns = time_sku_data_with_datapoint_id.columns
    #     columns_without_id = [col for col in columns if col != "datapointID"]

    #     time_sku_feature_description_map["featureID"] = time_sku_feature_description.ids
    #     del time_sku_feature_description_map["description"]
    #     del time_sku_feature_description_map["companyID"]
    #     del time_sku_feature_description_map["var_type"]
    #     time_sku_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(time_sku_feature_description_map, time_sku_data_with_datapoint_id)
    #     time_sku_feature_map = time_sku_data_with_datapoint_id.merge(
    #         time_sku_feature_description_map, on="feature", how="left"
    #     )

    #     time_sku_feature_map["featureID"] = time_sku_feature_map["featureID"].astype("int")
    #     time_sku_feature_map["value"] = time_sku_feature_map["value"].astype("float")
    #     del time_sku_feature_map["feature"]

    #     logger.info("Writing time-sku features to the database")
    #     time_sku_features = TimeSkuFeatures(self.db, self.insertion_mode)

    #     time_sku_features.write_to_db_multi_row(time_sku_feature_map, save_ids=False, show_progress_bar=True)

    #     return time_sku_data_with_datapoint_id, time_sku_feature_description_map

    # def write_flags(
    #     self,
    #     flags: pd.DataFrame,
    #     company_object: Companies,
    #     time_sku_data_with_datapoint_id: pd.DataFrame,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[Flags]:
    #     """
    #     Create and write flags.
    #     """

    #     flags = clean_and_check_flags(flags, copy=True)
    #     company_id = company_object.ids

    #     flag_levels_list = [lvl.value for lvl in FlagLevels]

    #     # create dataframe with columns "name" (flag_levels_list, three separate rows), "description" ("flag indicating ..."), "companyID", "var_type" ("binary"), feature_type ("time_sku")
    #     flag_levels_map = {
    #         "name": flag_levels_list,
    #         "description": ["flag indicating ..."] * len(flag_levels_list),
    #         "companyID": [company_id] * len(flag_levels_list),
    #         "var_type": ["binary"] * len(flag_levels_list),
    #         "feature_type": ["time_sku"] * len(flag_levels_list),
    #     }
    #     flag_levels_map = pd.DataFrame(flag_levels_map)

    #     time_sku_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     time_sku_feature_description.write_to_db_multi_row(flag_levels_map, save_ids=True)
    #     flag_levels_map["featureID"] = time_sku_feature_description.ids
    #     del flag_levels_map["description"]
    #     del flag_levels_map["companyID"]
    #     del flag_levels_map["var_type"]
    #     flag_levels_map.rename(columns={"name": "feature"}, inplace=True)

    #     flags.rename(columns={"flag": "feature"}, inplace=True)
    #     flags["value"] = "1"
    #     flags = flags.merge(flag_levels_map, on="feature", how="left")

    #     # convert dates to string on daily granularity
    #     flags["date"] = pd.to_datetime(flags["date"]).dt.date

    #     query = f"""
    #         SELECT "product_name", "store_name", "date", "datapointID"
    #         FROM datapoints_full_definition
    #         WHERE product_name = %s
    #         AND date = %s
    #         AND store_name = %s
    #         AND "companyID" = %s
    #     """

    #     flag_ids = []
    #     rows_to_remove = []

    #     args = list(zip(flags["product"], flags["date"].astype("string"), flags["store"], [company_id] * len(flags)))
    #     args = tuple(args)

    #     logger.info("Retrieving datapoint IDs for flags ...")
    #     # change this to get a one-shot query instead of line-by-line.
    #     datapoint_ids = self.db.execute_multi_query(query, args, fetchall=True, show_progress_bar=True)

    #     # check if datapoint_ids are empty
    #     if datapoint_ids:
    #         datapoint_ids = [
    #             datapoint_id[0] if len(datapoint_id) > 0 else datapoint_id for datapoint_id in datapoint_ids
    #         ]

    #     # create pandas
    #     datapoint_ids = pd.DataFrame(datapoint_ids, columns=["product", "store", "date", "datapointID"])

    #     # merge the datapoint ids back to the flags
    #     flags = flags.merge(datapoint_ids, on=["product", "date", "store"], how="left")

    #     # check if all flags have a datapointID
    #     if flags["datapointID"].isna().sum() > 0:
    #         raise ValueError(
    #             f"Could not find a datapoint for {flags['datapointID'].isna().sum()} flags.\n"
    #             "Ensure that sales are set to 0 for all dates where not_for_sale is true and that sales are set to NaN where no value is available."
    #         )

    #     del flags["product"]
    #     del flags["store"]
    #     del flags["date"]
    #     del flags["feature"]
    #     del flags["feature_type"]

    #     flags["value"] = flags["value"].astype("float")

    #     time_sku_features_object = TimeSkuFeatures(self.db, self.insertion_mode)
    #     time_sku_features_object.write_to_db_multi_row(flags, save_ids=False, show_progress_bar=True)

    #     return Flags

    # #################################### Optional data #############################################

    # def write_store_data(
    #     self,
    #     store_feature_description_map: pd.DataFrame,
    #     store_feature_map: pd.DataFrame,
    #     store_object: Stores,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, StoreFeatures]:
    #     """
    #     Create and write static store features.

    #     """

    #     store_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     store_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     store_features = StoreFeatures(self.db, self.insertion_mode)

    #     if len(store_feature_description_map) == 0:
    #         logger.warning("Did not receive any store features, skipping ...")
    #         return store_feature_description, store_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     store_feature_description_map = clean_and_check_feature_description_map(
    #         store_feature_description_map, store_feature_map, copy=True
    #     )
    #     store_feature_description_map["companyID"] = company_id
    #     store_feature_description_map, levels = self.extract_levels(store_feature_description_map)

    #     store_feature_description_map["feature_type"] = "store"
    #     store_feature_description.write_to_db_multi_row(store_feature_description_map, save_ids=True)
    #     del store_feature_description_map["feature_type"]

    #     levels = self.prep_levels(store_feature_description, store_feature_description_map, levels)
    #     store_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     store_feature_map = clean_and_check_store_feature_data(store_feature_map, copy=True)

    #     store_feature_description_map["featureID"] = store_feature_description.ids
    #     del store_feature_description_map["description"]
    #     del store_feature_description_map["companyID"]
    #     del store_feature_description_map["var_type"]
    #     store_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(store_feature_description_map, store_feature_map)
    #     store_feature_map = store_feature_map.merge(
    #         store_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del store_feature_map["feature"]

    #     store_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_id,
    #         table_name="stores",
    #         column_name="name",
    #         datapoints=store_feature_map["store"].unique(),
    #         output_column_name="store",
    #         output_column_ID="storeID",
    #     )

    #     store_feature_map = store_feature_map.merge(store_ids_df, left_on="store", right_on="store", how="left")
    #     del store_feature_map["store"]

    #     store_features.write_to_db_multi_row(store_feature_map, save_ids=False, show_progress_bar=False)

    #     return store_feature_description, store_features

    # def write_product_data(
    #     self,
    #     product_feature_description_map: pd.DataFrame,
    #     product_feature_map: pd.DataFrame,
    #     product_object: Stores,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, ProductFeatures]:
    #     """Create and write static product features."""

    #     product_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     product_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     product_features = ProductFeatures(self.db, self.insertion_mode)

    #     if len(product_feature_description_map) == 0:
    #         logger.warning("Did not receive any product features, skipping ...")
    #         return product_feature_description, product_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     product_feature_description_map = clean_and_check_feature_description_map(
    #         product_feature_description_map, product_feature_map, copy=True
    #     )
    #     product_feature_description_map["companyID"] = company_id
    #     product_feature_description_map, levels = self.extract_levels(product_feature_description_map)

    #     product_feature_description_map["feature_type"] = "product"
    #     product_feature_description.write_to_db_multi_row(product_feature_description_map, save_ids=True)
    #     del product_feature_description_map["feature_type"]

    #     levels = self.prep_levels(product_feature_description, product_feature_description_map, levels)
    #     product_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     product_feature_map = clean_and_check_product_feature_data(product_feature_map, copy=True)

    #     product_feature_description_map["featureID"] = product_feature_description.ids
    #     del product_feature_description_map["description"]
    #     del product_feature_description_map["companyID"]
    #     del product_feature_description_map["var_type"]
    #     product_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(product_feature_description_map, product_feature_map)
    #     product_feature_map = product_feature_map.merge(
    #         product_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del product_feature_map["feature"]

    #     product_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_object.ids,
    #         table_name="products",
    #         column_name="name",
    #         datapoints=product_feature_map["product"].unique(),
    #         output_column_name="product",
    #         output_column_ID="productID",
    #     )

    #     product_feature_map = product_feature_map.merge(
    #         product_ids_df, left_on="product", right_on="product", how="left"
    #     )
    #     del product_feature_map["product"]

    #     product_features.write_to_db_multi_row(product_feature_map, save_ids=False, show_progress_bar=True)

    #     return product_feature_description, product_features

    # def write_sku_data(
    #     self,
    #     sku_feature_description_map: pd.DataFrame,
    #     sku_feature_map: pd.DataFrame,
    #     sku_object: Stores,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, SkuFeatures]:
    #     """
    #     Create and write static store features.

    #     """

    #     sku_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     sku_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     sku_features = SKUFeatures(self.db, self.insertion_mode)

    #     if len(sku_feature_description_map) == 0:
    #         logger.warning("Did not receive any SKU features, skipping ...")
    #         return sku_feature_description, sku_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     sku_feature_description_map = clean_and_check_feature_description_map(
    #         sku_feature_description_map, sku_feature_map, copy=True
    #     )
    #     sku_feature_description_map["companyID"] = company_id
    #     sku_feature_description_map, levels = self.extract_levels(sku_feature_description_map)

    #     sku_feature_description_map["feature_type"] = "sku"
    #     sku_feature_description.write_to_db_multi_row(sku_feature_description_map, save_ids=True)
    #     del sku_feature_description_map["feature_type"]

    #     levels = self.prep_levels(sku_feature_description, sku_feature_description_map, levels)
    #     sku_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     sku_feature_map = clean_and_check_sku_feature_data(sku_feature_map, copy=True)

    #     sku_feature_description_map["featureID"] = sku_feature_description.ids
    #     del sku_feature_description_map["description"]
    #     del sku_feature_description_map["companyID"]
    #     del sku_feature_description_map["var_type"]
    #     sku_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(sku_feature_description_map, sku_feature_map)
    #     sku_feature_map = sku_feature_map.merge(
    #         sku_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del sku_feature_map["feature"]

    #     product_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_object.ids,
    #         table_name="products",
    #         column_name="name",
    #         datapoints=sku_feature_map["product"].unique(),
    #         output_column_name="product",
    #         output_column_ID="productID",
    #     )
    #     store_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_object.ids,
    #         table_name="stores",
    #         column_name="name",
    #         datapoints=sku_feature_map["store"].unique(),
    #         output_column_name="store",
    #         output_column_ID="storeID",
    #     )

    #     sku_feature_map = sku_feature_map.merge(product_ids_df, left_on="product", right_on="product", how="left")
    #     sku_feature_map = sku_feature_map.merge(store_ids_df, left_on="store", right_on="store", how="left")

    #     del sku_feature_map["product"]
    #     del sku_feature_map["store"]

    #     store_ids = sku_feature_map["storeID"].unique().tolist()
    #     product_ids = sku_feature_map["productID"].unique().tolist()

    #     condition = f"""
    #         "companyID" = '{company_id}' AND "storeID" IN ({", ".join([f"'{store_id}'" for store_id in store_ids])}) AND "productID" IN ({", ".join([f"'{product_id}'" for product_id in product_ids])})
    #     """

    #     sku_ids_df = retrieve_data(
    #         self.db, """ "sku_table_with_companyID" """, ["ID", "storeID", "productID"], condition=condition
    #     )
    #     sku_ids_df = pd.DataFrame(sku_ids_df, columns=["skuID", "storeID", "productID"])

    #     sku_feature_map = sku_feature_map.merge(
    #         sku_ids_df, left_on=["storeID", "productID"], right_on=["storeID", "productID"], how="left"
    #     )
    #     del sku_feature_map["storeID"]
    #     del sku_feature_map["productID"]

    #     sku_features.write_to_db_multi_row(sku_feature_map, save_ids=False, show_progress_bar=True)

    #     return sku_feature_description, sku_features

    # def write_time_product_data(
    #     self,
    #     time_product_feature_description_map: pd.DataFrame,
    #     time_product_feature_map: pd.DataFrame,
    #     product_object: Products,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, TimeProductFeatures]:
    #     """

    #     Create and write time-product features.

    #     """

    #     time_product_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     time_product_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     time_product_features = TimeProductFeatures(self.db, self.insertion_mode)

    #     if len(time_product_feature_description_map) == 0:
    #         logger.warning("Did not receive any time-product features, skipping ...")
    #         return time_product_feature_description, time_product_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     time_product_feature_description_map = clean_and_check_feature_description_map(
    #         time_product_feature_description_map, time_product_feature_map, copy=True
    #     )
    #     time_product_feature_description_map["companyID"] = company_id
    #     time_product_feature_description_map, levels = self.extract_levels(time_product_feature_description_map)

    #     time_product_feature_description_map["feature_type"] = "time_product"
    #     time_product_feature_description.write_to_db_multi_row(time_product_feature_description_map, save_ids=True)
    #     del time_product_feature_description_map["feature_type"]

    #     levels = self.prep_levels(time_product_feature_description, time_product_feature_description_map, levels)
    #     time_product_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     time_product_feature_map = clean_and_check_time_product_feature_data(time_product_feature_map, copy=True)

    #     time_product_feature_description_map["featureID"] = time_product_feature_description.ids
    #     del time_product_feature_description_map["description"]
    #     del time_product_feature_description_map["companyID"]
    #     del time_product_feature_description_map["var_type"]
    #     time_product_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(time_product_feature_description_map, time_product_feature_map)
    #     time_product_feature_map = time_product_feature_map.merge(
    #         time_product_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del time_product_feature_map["feature"]

    #     product_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_object.ids,
    #         table_name="products",
    #         column_name="name",
    #         datapoints=time_product_feature_map["product"].unique(),
    #         output_column_name="product",
    #         output_column_ID="productID",
    #     )

    #     time_product_feature_map = time_product_feature_map.merge(
    #         product_ids_df, left_on="product", right_on="product", how="left"
    #     )
    #     del time_product_feature_map["product"]

    #     unique_dates = time_product_feature_map["date"].unique().tolist()
    #     unique_dates = [str(date.date()) for date in unique_dates]

    #     date_ids_df = get_data_ids(
    #         self.db, table_name="dates", column_name="date", datapoints=unique_dates, output_column_ID="dateID"
    #     )
    #     date_ids_df["date"] = pd.to_datetime(date_ids_df["date"])

    #     time_product_feature_map = time_product_feature_map.merge(
    #         date_ids_df, left_on="date", right_on="date", how="left"
    #     )
    #     del time_product_feature_map["date"]

    #     time_product_features.write_to_db_multi_row(time_product_feature_map, save_ids=False, show_progress_bar=True)

    #     return time_product_feature_description, time_product_features

    # def write_time_region_data(
    #     self,
    #     time_region_feature_description_map: pd.DataFrame,
    #     time_region_feature_map: pd.DataFrame,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, TimeRegionFeatures]:
    #     """Create and write time-region features."""

    #     time_region_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     time_region_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     time_region_features = TimeRegionFeatures(self.db, self.insertion_mode)

    #     if len(time_region_feature_description_map) == 0:
    #         logger.warning("Did not receive any time-region features, skipping ...")
    #         return time_region_feature_description, time_region_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     time_region_feature_description_map = clean_and_check_feature_description_map(
    #         time_region_feature_description_map, time_region_feature_map, copy=True
    #     )
    #     time_region_feature_description_map["companyID"] = company_id
    #     time_region_feature_description_map, levels = self.extract_levels(time_region_feature_description_map)

    #     time_region_feature_description_map["feature_type"] = "time_region"
    #     time_region_feature_description.write_to_db_multi_row(time_region_feature_description_map, save_ids=True)
    #     del time_region_feature_description_map["feature_type"]

    #     levels = self.prep_levels(time_region_feature_description, time_region_feature_description_map, levels)
    #     time_region_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     time_region_feature_map = clean_and_check_time_region_feature_data(time_region_feature_map, copy=True)

    #     countries = time_region_feature_map["country"].unique()

    #     if len(time_region_feature_map.columns) == 5:
    #         for column_name in time_region_feature_map.columns:
    #             if column_name in ["date", "country", "feature", "value"]:
    #                 continue
    #             region_type = column_name

    #         subsets = []
    #         for country in countries:
    #             country_data = time_region_feature_map[time_region_feature_map["country"] == country]
    #             country_id = retrieve_data(self.db, "regions", "ID", f"abbreviation='{country}' AND type='country'")
    #             time_region_feature_map_subset = time_region_feature_map[time_region_feature_map["country"] == country]
    #             if not country_id:
    #                 raise ValueError(
    #                     f"Country {country} not found in the database. Ensure the General Data pipeline is executed first. See step 3 in: https://github.com/d3group/foundry-master/blob/main/documentation/new_db_set_up.md"
    #                 )
    #             else:
    #                 country_id = country_id[0][0]

    #             condition = f"""
    #                 "country" = '{country_id}'
    #                 AND
    #                 "abbreviation" IN ({", ".join([f"'{region}'" for region in country_data[region_type].unique()])})
    #             """
    #             region_ids = retrieve_data(self.db, "regions", ["ID", "abbreviation"], condition=condition)

    #             # convert to DataFrame
    #             region_ids_df = pd.DataFrame(region_ids, columns=["regionID", "abbreviation"])
    #             region_ids_df.rename(columns={"abbreviation": region_type}, inplace=True)
    #             time_region_feature_map_subset = time_region_feature_map_subset.merge(
    #                 region_ids_df, left_on=region_type, right_on=region_type, how="left"
    #             )
    #             subsets.append(time_region_feature_map_subset)

    #         time_region_feature_map = pd.concat(subsets)

    #         del time_region_feature_map["country"]
    #         del time_region_feature_map[region_type]

    #     elif len(time_region_feature_map.columns) == 4:
    #         unique_countries = time_region_feature_map["country"].unique()
    #         condition = f"""
    #             "abbreviation" IN ({", ".join([f"'{country}'" for country in unique_countries])})
    #             AND
    #             "type" = 'country'
    #         """
    #         country_ids = retrieve_data(self.db, "regions", ["ID", "abbreviation"], condition=condition)
    #         country_ids_df = pd.DataFrame(country_ids, columns=["countryID", "abbreviation"])
    #         country_ids_df.rename(columns={"abbreviation": "country"}, inplace=True)

    #         time_region_feature_map = time_region_feature_map.merge(
    #             country_ids_df, left_on="country", right_on="country", how="left"
    #         )
    #         del time_region_feature_map["country"]
    #         # rename countryID to regionID
    #         time_region_feature_map.rename(columns={"countryID": "regionID"}, inplace=True)

    #     else:
    #         raise ValueError(
    #             f"Time-region feature map has {len(time_region_feature_map.columns)} columns. Expected 4 or 5 columns."
    #         )

    #     unique_feature_names = time_region_feature_map["feature"].unique()

    #     time_region_feature_description_map["featureID"] = time_region_feature_description.ids
    #     del time_region_feature_description_map["description"]
    #     del time_region_feature_description_map["companyID"]
    #     del time_region_feature_description_map["var_type"]
    #     time_region_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(time_region_feature_description_map, time_region_feature_map)
    #     time_region_feature_map = time_region_feature_map.merge(
    #         time_region_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del time_region_feature_map["feature"]

    #     unique_dates = time_region_feature_map["date"].unique().tolist()
    #     unique_dates = [str(date.date()) for date in unique_dates]

    #     date_ids_df = get_data_ids(
    #         self.db, table_name="dates", column_name="date", datapoints=unique_dates, output_column_ID="dateID"
    #     )
    #     date_ids_df["date"] = pd.to_datetime(date_ids_df["date"])

    #     time_region_feature_map = time_region_feature_map.merge(
    #         date_ids_df, left_on="date", right_on="date", how="left"
    #     )
    #     del time_region_feature_map["date"]

    #     time_region_features.write_to_db_multi_row(time_region_feature_map, save_ids=False, show_progress_bar=False)

    #     return time_region_feature_description, time_region_features

    # def write_time_store_data(
    #     self,
    #     time_store_feature_description_map: pd.DataFrame,
    #     time_store_feature_map: pd.DataFrame,
    #     store_object: Stores,
    #     company_object: Companies,
    #     *,
    #     check_passed: bool,
    # ) -> t.Tuple[FeatureDescriptions, TimeStoreFeatures]:
    #     """
    #     Create and write time-store features.
    #     """

    #     time_store_feature_description = FeatureDescriptions(self.db, self.insertion_mode)
    #     time_store_feature_levels = FeatureLevels(self.db, self.insertion_mode)
    #     time_store_features = TimeStoreFeatures(self.db, self.insertion_mode)

    #     if len(time_store_feature_description_map) == 0:
    #         logger.warning("Did not receive any time-store features, skipping ...")
    #         return time_store_feature_description, time_store_features

    #     ####### Prepare description
    #     company_id = company_object.ids
    #     time_store_feature_description_map = clean_and_check_feature_description_map(
    #         time_store_feature_description_map, time_store_feature_map, copy=True
    #     )
    #     time_store_feature_description_map["companyID"] = company_id
    #     time_store_feature_description_map, levels = self.extract_levels(time_store_feature_description_map)

    #     time_store_feature_description_map["feature_type"] = "time_store"
    #     time_store_feature_description.write_to_db_multi_row(time_store_feature_description_map, save_ids=True)
    #     del time_store_feature_description_map["feature_type"]

    #     levels = self.prep_levels(time_store_feature_description, time_store_feature_description_map, levels)
    #     time_store_feature_levels.write_to_db_multi_row(levels, save_ids=False)

    #     time_store_feature_map = clean_and_check_time_store_feature_data(time_store_feature_map, copy=True)

    #     time_store_feature_description_map["featureID"] = time_store_feature_description.ids
    #     del time_store_feature_description_map["description"]
    #     del time_store_feature_description_map["companyID"]
    #     del time_store_feature_description_map["var_type"]
    #     time_store_feature_description_map.rename(columns={"name": "feature"}, inplace=True)

    #     test_features(time_store_feature_description_map, time_store_feature_map)
    #     time_store_feature_map = time_store_feature_map.merge(
    #         time_store_feature_description_map, left_on="feature", right_on="feature", how="left"
    #     )
    #     del time_store_feature_map["feature"]

    #     store_ids_df = get_data_ids_by_company(
    #         self.db,
    #         company_id=company_id,
    #         table_name="stores",
    #         column_name="name",
    #         datapoints=time_store_feature_map["store"].unique(),
    #         output_column_name="store",
    #         output_column_ID="storeID",
    #     )

    #     time_store_feature_map = time_store_feature_map.merge(
    #         store_ids_df, left_on="store", right_on="store", how="left"
    #     )
    #     del time_store_feature_map["store"]

    #     # get dates
    #     unique_dates = time_store_feature_map["date"].unique().tolist()
    #     unique_dates = [str(date.date()) for date in unique_dates]

    #     date_ids_df = get_data_ids(
    #         self.db, table_name="dates", column_name="date", datapoints=unique_dates, output_column_ID="dateID"
    #     )
    #     date_ids_df["date"] = pd.to_datetime(date_ids_df["date"])

    #     time_store_feature_map = time_store_feature_map.merge(date_ids_df, left_on="date", right_on="date", how="left")
    #     del time_store_feature_map["date"]

    #     logger.info("Writing time-store features to the database")
    #     time_store_features.write_to_db_multi_row(time_store_feature_map, save_ids=False, show_progress_bar=True)

    #     return time_store_feature_description, time_store_features
