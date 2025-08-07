import logging
import time
import typing as t
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType

import polars as pl
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from sqlalchemy import create_engine, text, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import bindparam
from tqdm import tqdm

logger = logging.getLogger(__name__)


class SQLAlchemyDatabase:
    """
    SQLAlchemy-based database management class to replace the legacy psycopg2 implementation.
    Provides three ways to configure database credentials and modern session management.
    """

    def __init__(
        self,
        *,
        autocommit: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        connect_args: dict | None = None,
    ) -> None:
        self.engine: Engine | None = None
        self.SessionLocal: t.Callable[[], Session] | None = None
        self.autocommit = autocommit
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        self.connect_args = connect_args or {}

    def _create_engine(self, connection_string: str) -> Engine:
        return create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,
            echo=self.echo,
            connect_args=self.connect_args,
            pool_reset_on_return="commit",
            execution_options={"isolation_level": "READ_COMMITTED"},
        )

    @classmethod
    def from_kedro(cls, **kwargs) -> "SQLAlchemyDatabase":
        conf_path = str(Path(settings.CONF_SOURCE))
        conf_loader = OmegaConfigLoader(conf_source=conf_path)

        try:
            db_credentials = conf_loader["credentials"]["postgres"]
        except KeyError as err:
            raise KeyError("Missing 'postgres' credentials in Kedro config.") from err

        connection_string = db_credentials["con"]
        instance = cls(**kwargs)
        instance.engine = instance._create_engine(connection_string)
        instance.SessionLocal = sessionmaker(
            bind=instance.engine,
            autocommit=instance.autocommit,
            autoflush=not instance.autocommit,
        )
        return instance

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        **kwargs,
    ) -> "SQLAlchemyDatabase":
        instance = cls(**kwargs)
        instance.engine = instance._create_engine(connection_string)
        instance.SessionLocal = sessionmaker(
            bind=instance.engine,
            autocommit=instance.autocommit,
            autoflush=not instance.autocommit,
        )
        return instance

    @classmethod
    def from_parameters(
        cls,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        **kwargs,
    ) -> "SQLAlchemyDatabase":
        connection_params = {}
        instance_params = {}

        for key, value in kwargs.items():
            if key in ["sslmode", "application_name", "connect_timeout", "sslcert", "sslkey"]:
                connection_params[key] = value
            else:
                instance_params[key] = value

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        if connection_params:
            params = "&".join([f"{k}={v}" for k, v in connection_params.items()])
            connection_string += f"?{params}"

        instance = cls(**instance_params)
        instance.engine = instance._create_engine(connection_string)
        instance.SessionLocal = sessionmaker(
            bind=instance.engine,
            autocommit=instance.autocommit,
            autoflush=not instance.autocommit,
        )
        return instance

    @contextmanager
    def get_session(self, *, read_only: bool = False) -> t.Generator[Session, None, None]:
        if not self.SessionLocal:
            raise RuntimeError(
                "Database not configured. Call one of the factory methods "
                "(from_kedro, from_connection_string, from_parameters) first.",
            )

        session = self.SessionLocal()

        try:
            if read_only:
                session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
            if not self.autocommit and not read_only:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            logger.exception("[DB Test Failed]")
            return False
        else:
            return True

    def health_check(self) -> dict[str, t.Any]:
        try:
            start_time = time.time()

            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                result = session.execute(text("SELECT current_timestamp, version()")).fetchone()
                db_time = result[0] if result else None
                db_version = result[1] if result else None

            response_time = time.time() - start_time
            pool_status = {}
            if self.engine and hasattr(self.engine, "pool"):
                pool = self.engine.pool
                pool_status = {
                    "pool_size": pool.size(),
                    "checked_out_connections": pool.checkedout(),
                    "overflow_connections": pool.overflow(),
                    "invalid_connections": pool.invalidated(),
                }

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "database_time": str(db_time) if db_time else None,
                "database_version": db_version.split("\n")[0] if db_version else None,
                "pool_status": pool_status,
                "autocommit_mode": self.autocommit,
                "timestamp": time.time(),
            }

        except SQLAlchemyError as e:
            return {
                "status": "unhealthy",
                "error": f"Database error: {e!s}",
                "timestamp": time.time(),
            }

    def get_primary_unique_constraint(self, model_class: DeclarativeMeta) -> list[str]:
        if hasattr(model_class, "__unique_keys__"):
            return model_class.__unique_keys__
        msg = f"Model class {model_class.__name__} does not define __unique_keys__ attribute."
        raise ValueError(msg)

    def _validate_single_line_input(
        self,
        model_class: DeclarativeMeta,
        data: dict[str, t.Any],
    ) -> None:
        """Validate the input data is a dict representing a single row."""
        if not isinstance(data, dict):
            raise TypeError("`data` must be a dict of column names to values.")
        table = model_class.__table__
        model_columns = {col.name for col in table.columns}
        extra_keys = set(data.keys()) - model_columns
        if extra_keys:
            msg = f"Unexpected columns in data: {extra_keys}"
            raise ValueError(msg)

    def handle_insertion_single_line(
        self,
        model_class: DeclarativeMeta,
        data: dict[str, t.Any],
        mode: t.Literal["RAISE", "IGNORE", "UPDATE"],
        *,
        returning_id: bool = False,
    ) -> int | None:
        """
        Unified single-call insert/upsert with explicit modes.
         - RAISE:   plain INSERT, error on conflict
         - IGNORE:  INSERT ... ON CONFLICT DO NOTHING
         - UPDATE:  INSERT ... ON CONFLICT DO UPDATE (excluding PK cols).

        Conflict logic targets the model's primary key columns.

        Args:
            model_class: SQLAlchemy model class
            data: Dictionary of column names to values
            mode: Conflict resolution strategy ("RAISE", "IGNORE", "UPDATE")
            returning_id: If True, returns the record ID; if False, returns None

        Returns:
            int: the primary key (id) of the processed record if returning_id=True
            None: if returning_id=False

        """
        # validate that data keys match the model
        self._validate_single_line_input(model_class, data)
        self.check_mode(mode)

        p_unique_key_columns = self.get_primary_unique_constraint(model_class)

        # build base INSERT statement
        stmt = insert(model_class).values(**data)

        # apply conflict clause per mode
        if mode == "IGNORE":
            stmt = stmt.on_conflict_do_nothing(index_elements=p_unique_key_columns)
            with self.get_session() as session:
                if returning_id:
                    stmt_ret = stmt.returning(model_class.id)
                    record_id = session.execute(stmt_ret).scalar()
                    if record_id is None:
                        # Find existing record that caused the conflict
                        pk_filter = {pk: data[pk] for pk in p_unique_key_columns if pk in data}
                        record_id = session.query(model_class.id).filter_by(**pk_filter).scalar()
                        if record_id is None:
                            raise RuntimeError("Record not found after conflict - possible race condition")
                    return record_id
                session.execute(stmt)
                return None
        elif mode == "UPDATE":
            update_data = {k: getattr(stmt.excluded, k) for k in data if k not in p_unique_key_columns}
            if not update_data:  # All columns are primary keys
                # Convert to IGNORE behavior since nothing to update
                stmt = stmt.on_conflict_do_nothing(index_elements=p_unique_key_columns)
            else:
                stmt = stmt.on_conflict_do_update(
                    index_elements=p_unique_key_columns,
                    set_=update_data,
                )
        elif mode == "RAISE":
            # no ON CONFLICT clause; let DB raise on duplicates
            pass
        else:
            msg = f"Unsupported insertion mode: '{mode}'"
            raise ValueError(msg)

        # UPDATE or RAISE paths: execute and optionally fetch the ID
        with self.get_session() as session:
            if returning_id:
                stmt = stmt.returning(model_class.id)
                return session.execute(stmt).scalar()
            session.execute(stmt)
            return None

    def handle_insertion_multi_line(
        self,
        model_class: DeclarativeMeta,
        data: pl.DataFrame,
        mode: t.Literal["RAISE", "IGNORE", "UPDATE"],
        *,
        threshold_for_copy: int = 100_000_000_000,  # temporarily do not use copy
        returning_id: bool = False,
    ) -> pl.DataFrame | None:
        """
        Validate a Polars DataFrame against the model schema, then delegate
        to the bulk-insert implementation.
        """
        self.check_mode(mode)
        # 1. Basic type & column-name checks
        if not isinstance(data, pl.DataFrame):
            raise TypeError("`data` must be a Polars DataFrame.")

        if len(data) == 0:
            logger.warning("Empty DataFrame provided, nothing to insert.")
            return None

        if len(data) >= threshold_for_copy:
            return self.handle_insertion_multi_line_copy(
                model_class,
                data,
                mode,
                returning_id=returning_id,
            )

        return self.handle_insertion_multi_line_bulk(
            model_class,
            data,
            mode,
            returning_id=returning_id,
        )

    def handle_insertion_multi_line_bulk(
        self,
        model_class: DeclarativeMeta,
        data: pl.DataFrame,
        mode: t.Literal["RAISE", "IGNORE", "UPDATE"],
        *,
        chunk_size: int = 1000,
        returning_id: bool = False,
    ) -> pl.DataFrame | None:
        """
        Perform bulk upserts in chunks of `chunk_size` rows using SQLAlchemy Core.

        Writes data first, then—if `returning_id=True`—fetches all primary keys
        for the provided unique-key combinations in one go.
        Returns a DataFrame of unique-key columns plus "id" if requested,
        otherwise returns None.
        """
        # Determine unique-key columns
        p_unique_key_columns = self.get_primary_unique_constraint(model_class)
        total_rows = data.height
        total_chunks = (total_rows + chunk_size - 1) // chunk_size

        logger.info("Starting bulk insert of %d rows in %d chunks of size %d", total_rows, total_chunks, chunk_size)
        # Phase 1: Write all rows in chunks
        table_name = model_class.__table__.name
        with self.get_session() as session:
            for offset in tqdm(
                range(0, total_rows, chunk_size),
                total=total_chunks,
                desc=f"Writing to {table_name} with chunk size {chunk_size}",
                unit="chunk",
            ):
                chunk_df = data.slice(offset, chunk_size)
                records = chunk_df.to_dicts()

                # Build INSERT statement for only the columns present in the DataFrame
                stmt = insert(model_class.__table__).values({col: bindparam(col) for col in chunk_df.columns})
                if mode == "IGNORE":
                    stmt = stmt.on_conflict_do_nothing(index_elements=p_unique_key_columns)
                elif mode == "UPDATE":
                    update_cols = [c for c in chunk_df.columns if c not in p_unique_key_columns]
                    if update_cols:
                        stmt = stmt.on_conflict_do_update(
                            index_elements=p_unique_key_columns, set_={col: stmt.excluded[col] for col in update_cols}
                        )
                    else:
                        stmt = stmt.on_conflict_do_nothing(index_elements=p_unique_key_columns)
                elif mode == "RAISE":
                    pass  # No ON CONFLICT clause needed

                # Execute insertion
                session.execute(stmt, records)

        # Phase 2: Retrieve IDs if needed
        if returning_id:
            logger.info("Fetching IDs for unique keys: %s", p_unique_key_columns)
            # Collect unique-key tuples
            key_df = data.select(*p_unique_key_columns)

            # Query all matching IDs in one go
            with self.get_session() as session:
                # Map database column names to SQLAlchemy attributes
                unique_key_attrs = [self.get_column_attr_by_db_name(model_class, col) for col in p_unique_key_columns]

                query = session.query(
                    *unique_key_attrs,
                    model_class.id,
                )
                # filter by tuple IN
                key_tuples = [tuple(row) if len(p_unique_key_columns) > 1 else row[0] for row in key_df.rows()]
                if len(p_unique_key_columns) == 1:
                    col_attr = unique_key_attrs[0]
                    query = query.filter(col_attr.in_(key_tuples))
                else:
                    query = query.filter(tuple_(*unique_key_attrs).in_(key_tuples))
                results = query.all()

            # Build a Polars DataFrame of keys + id
            ids_df = pl.DataFrame([dict(zip([*p_unique_key_columns, "id"], row, strict=True)) for row in results])
            return ids_df

        return None

    def handle_insertion_multi_line_copy(
        self,
        model_class: DeclarativeMeta,
        data: pl.DataFrame,
        mode: t.Literal["RAISE", "IGNORE", "UPDATE"],
        *,
        chunk_size: int = 1_000_000,
        returning_id: bool = False,
    ) -> pl.DataFrame | None:
        raise NotImplementedError

    @staticmethod
    def get_column_attr_by_db_name(model_class: DeclarativeMeta, db_col_name: str) -> InstrumentedAttribute:
        """
        Map database column name to SQLAlchemy model attribute.

        This function resolves the mapping between database column names (e.g., "ID", "companyID", "regionID")
        and their corresponding SQLAlchemy model attributes (e.g., model.id, model.company_id, model.region_id).
        This is necessary because SQLAlchemy models often use Python naming conventions for attributes
        while maintaining the original database column names.

        Args:
            model_class: SQLAlchemy declarative model class
            db_col_name: Database column name as stored in the database schema

        Returns:
            SQLAlchemy InstrumentedAttribute that can be used in queries

        Raises:
            AttributeError: If no matching attribute is found for the given database column name

        Example:
            >>> # For a model with: id = Column("ID", Integer, primary_key=True)
            >>> attr = get_column_attr_by_db_name(MyModel, "ID")
            >>> # Returns MyModel.id (InstrumentedAttribute)
            >>> query = session.query(attr)  # Can be used in queries

        """
        # Check all columns in the model's table to find the matching attribute
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if (
                hasattr(attr, "property")
                and hasattr(attr.property, "columns")
                and attr.property.columns[0].name == db_col_name
            ):
                # This is a SQLAlchemy column that matches the database column name
                return attr
        msg = f"No attribute found for database column '{db_col_name}' in {model_class.__name__}"
        raise AttributeError(msg)

    @staticmethod
    def check_mode(mode: t.Literal["RAISE", "IGNORE", "UPDATE"]) -> None:
        """
        Validate the insertion mode is one of the supported types.
        Raises ValueError if unsupported mode is provided.
        """
        if mode not in {"RAISE", "IGNORE", "UPDATE"}:
            msg = f"Unsupported insertion mode: '{mode}'"
            raise ValueError(msg)

    def close(self) -> None:
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None

    def __enter__(self) -> None:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
