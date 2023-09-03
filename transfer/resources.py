from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from loguru import logger

from . import config
from .file_utils import remove_expired_files

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:  # noqa: ARG001
    await startup()
    try:
        yield
    finally:
        await shutdown()


async def startup() -> None:
    show_config()
    # insert here calls to connect to database and other services
    scheduler.add_job(remove_expired_files, 'interval', days=1)
    scheduler.start()
    logger.info('started...')


async def shutdown() -> None:
    # insert here calls to disconnect from database and other services
    scheduler.shutdown()
    logger.info('...shutdown')


def show_config() -> None:
    config_vars = {key: getattr(config, key) for key in sorted(dir(config)) if key.isupper()}
    logger.debug(config_vars)
