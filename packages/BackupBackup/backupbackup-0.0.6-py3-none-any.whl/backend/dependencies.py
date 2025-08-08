from functools import lru_cache
from logging import Logger
from typing import Optional

from backend.config import LoggerService, Settings


@lru_cache
def get_settings():
    return Settings()


# Global logger - initialized during lifespan
_logger: Optional[Logger] = None


def set_logger(logger: Logger) -> None:
    global _logger
    _logger = logger


@lru_cache
def get_logger() -> Logger:
    if _logger is None:
        return LoggerService.get_logger()
    return _logger
