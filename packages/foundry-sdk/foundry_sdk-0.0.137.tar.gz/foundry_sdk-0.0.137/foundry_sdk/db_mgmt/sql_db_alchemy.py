import time
import typing as t
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool


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
        except SQLAlchemyError as e:
            print(f"[DB Test Failed] {e}")
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
