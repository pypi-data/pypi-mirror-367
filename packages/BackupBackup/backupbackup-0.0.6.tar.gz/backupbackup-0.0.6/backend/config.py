import logging.config
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="FastAPI App BackupBackup")
    admin_email: str = "admin@backupbackup.ch"
    debug_mode: bool = False
    base_path: Path = Path(__file__).resolve().parent
    default_logger: str = "bb.debug"
    captcha_ttl: int = 300  # 5min
    possible_captcha_codes: List[str] = [
        "Leroy",
        "Vera",
        "Nic",
        "Felix",
        "Frederik",
        "Phil",
        "Jan",
        "Celine",
        "Mischa",
    ]

    database_url: str = "sqlite:///" + "database.db"

    redis_host: str = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port: int = os.getenv("REDIS_PORT", 6379)
    redis_db: int = os.getenv("REDIS_DB", 0)
    redis_decode_responses: bool = os.getenv("REDIS_HOST", True)
    redis_max_connections: int = 10

    secret_key: str = os.getenv("SECRET_KEY")
    web_domain_tld: str = os.getenv("WEB_DOMAIN_TLD", "127.0.0.1")
    hashing_algo: str = "HS256"
    access_token_expire_minutes: int = 30

    osa_provider: str = os.getenv("ACCOUNT_PROVIDER")
    osa_admin_key_location: str = os.getenv(
        "ACCOUNT_ADMIN_KEY_LOCATION", "/home/leroy/.ssh/id_rsa"
    )
    osa_base_path: str = os.getenv("ACCOUNT_BASE_PATH", "/data2/home/")
    osas: List[str] = [os.getenv("ACCOUNT_1"), os.getenv("ACCOUNT_2")]


class LoggerService:
    _instance: Optional[logging.Logger] = None
    _settings: Optional[Settings] = None
    _initialized: bool = False

    @classmethod
    def _ensure_logs_directory(cls, logs_path: Path) -> None:
        logs_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        if not cls._initialized:
            raise RuntimeError("Logger not initialized!")

        if name:
            return logging.getLogger(name)

        if cls._instance is None:
            raise RuntimeError("Default logger not initialized")

        return cls._instance

    @classmethod
    def initialize(
        cls, settings: Settings, name: Optional[str] = None
    ) -> logging.Logger:
        cls._settings = settings

        if not cls._initialized:
            try:
                config = cls._get_logging_config(settings)
                logging.config.dictConfig(config)
                cls._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize logging: {e}")

        logger_name = name or settings.default_logger
        logger = logging.getLogger(logger_name)

        if cls._instance is None and not name:
            cls._instance = logger

        return logger

    @classmethod
    def _get_logging_config(cls, settings: Settings) -> Dict[str, Any]:
        logs_path = settings.base_path / "logs"
        cls._ensure_logs_directory(logs_path)
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "format": "%(asctime)s - %(name)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "level": "DEBUG",
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(logs_path / "app.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
                "access_file": {
                    "level": "DEBUG",
                    "formatter": "access",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(logs_path / "access.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                settings.app_name: {
                    "handlers": ["console", "file", "access_file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console", "access_file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn.asgi": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console", "file"]},
        }
