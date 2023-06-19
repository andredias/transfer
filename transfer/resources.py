from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from . import config
from .file_utils import timeout_job

scheduler = AsyncIOScheduler()


async def startup() -> None:
    show_config()
    # insert here calls to connect to database and other services
    scheduler.add_job(timeout_job, 'interval', days=1)
    scheduler.start()
    logger.info('started...')


async def shutdown() -> None:
    # insert here calls to disconnect from database and other services
    scheduler.shutdown()
    logger.info('...shutdown')


def show_config() -> None:
    config_vars = {key: getattr(config, key) for key in sorted(dir(config)) if key.isupper()}
    logger.debug(config_vars)
