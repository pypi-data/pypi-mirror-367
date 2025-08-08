from logging import Logger
from sqlite3 import OperationalError
from typing import Generator, Optional

from redis import ConnectionPool, Redis
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from backend.dependencies import Settings, get_settings


class DatabaseManager:
    def __init__(self, settings: Settings, logger: Logger):
        self.settings = settings
        self.logger = logger
        self._engine: Optional[Engine] = None
        self._redis_pool: Optional[ConnectionPool] = None
        self._tables_created: bool = False

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            connect_args = {}
            if "sqlite" in self.settings.database_url:
                connect_args["check_same_thread"] = False

            self._engine = create_engine(
                self.settings.database_url,
                connect_args=connect_args,
                echo=self.settings.debug_mode,
            )

        return self._engine

    @property
    def redis_pool(self) -> Optional[ConnectionPool]:
        if self._redis_pool is None:
            try:
                self._redis_pool = ConnectionPool(
                    host=self.settings.redis_host,
                    port=self.settings.redis_port,
                    db=self.settings.redis_db,
                    decode_responses=self.settings.redis_decode_responses,
                    max_connections=self.settings.redis_max_connections,
                )
            except Exception as e:
                self.logger.error(f"Redis connection failed: {e}", exc_info=True)
                self._redis_pool = None

        return self._redis_pool

    def create_tables(self):
        if self._tables_created:
            return

        try:
            SQLModel.metadata.create_all(self.engine, checkfirst=True)
            self.logger.info("Database tables initialized successfully!")
        except OperationalError as e:
            if "already exists" in str(e).lower():
                self.logger.info("Database tables already exist, not recreating.")
            else:
                self.logger.error(
                    f"Error initializing database tables: {e}", exc_info=True
                )
                raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during database initialization: {e}", exc_info=True
            )
            raise
        finally:
            self._tables_created = True

    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session

    def get_redis_client(self) -> Optional[Redis]:
        if self.redis_pool:
            return Redis(connection_pool=self.redis_pool)
        return None

    def close(self):
        if self._engine:
            self._engine.dispose()
        if self._redis_pool:
            self._redis_pool.disconnect()


# Global database manager - initialized during lifespan
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    if _db_manager is None:
        raise RuntimeError(
            "Database manager not initialized. App not started properly."
        )
    return _db_manager


def get_db_engine() -> Optional[Engine]:
    db_manager = get_database_manager()
    return db_manager.engine


def get_db_session() -> Generator[Session, None, None]:
    """
    To be used only as dependency
    """
    db_manager = get_database_manager()
    yield from db_manager.get_session()


def get_redis_client() -> Optional[Redis]:
    db_manager = get_database_manager()
    return db_manager.get_redis_client()


def create_db_tables():
    db_manager = get_database_manager()
    db_manager.create_tables()


def initialize_database(logger: Logger) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        settings = get_settings()
        _db_manager = DatabaseManager(settings, logger)
    return _db_manager


def cleanup_database():
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
