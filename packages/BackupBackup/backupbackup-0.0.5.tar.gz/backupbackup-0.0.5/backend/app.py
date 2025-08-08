import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import schedule
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import LoggerService
from backend.database import (
    cleanup_database,
    create_db_tables,
    initialize_database,
)
from backend.dependencies import get_settings, set_logger
from backend.routes import router
from backend.seed import (
    create_default_member,
    create_default_osa,
    create_default_product,
)
from backend.utils import account_cleanup, get_account_usage


def schedule_runner():
    while True:
        schedule.run_pending()
        time.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup below here, before the "yield"
    settings = get_settings()
    logger = LoggerService.initialize(settings)
    set_logger(logger)
    logger.info("Application starting up ...")

    db_manager = initialize_database(logger)
    create_db_tables()
    create_default_member(db_manager.engine)
    create_default_product(db_manager.engine)
    create_default_osa(db_manager.engine, settings)
    scheduler_thread = threading.Thread(target=schedule_runner, daemon=True)
    scheduler_thread.start()
    schedule.every(1).minutes.do(
        account_cleanup, engine=db_manager.engine, logger=logger, settings=settings
    )
    schedule.every(1).minutes.do(
        get_account_usage, engine=db_manager.engine, logger=logger, settings=settings
    )
    yield
    # shutdown, below here
    cleanup_database()
    schedule.clear()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "templates" / "static"
app.mount(path="/static", app=StaticFiles(directory=str(static_dir)), name="static")
