from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi_limiter import FastAPILimiter
from loguru import logger
from redis.asyncio import Redis
from tenacity import RetryError, retry, stop_after_delay, wait_exponential

from . import config
from .file_utils import timeout_job

redis = Redis.from_url(config.REDIS_URL)
scheduler = AsyncIOScheduler()


async def startup() -> None:
    show_config()
    # insert here calls to connect to database and other services
    await connect_redis()
    await FastAPILimiter.init(redis)
    scheduler.add_job(timeout_job, 'interval', days=1)
    scheduler.start()
    logger.info('started...')


async def shutdown() -> None:
    # insert here calls to disconnect from database and other services
    await disconnect_redis()
    scheduler.shutdown()
    logger.info('...shutdown')


def show_config() -> None:
    config_vars = {key: getattr(config, key) for key in sorted(dir(config)) if key.isupper()}
    logger.debug(config_vars)


async def connect_redis() -> None:

    # test redis connection
    @retry(stop=stop_after_delay(3), wait=wait_exponential(multiplier=0.2))
    async def _connect_to_redis() -> None:
        logger.debug('Connecting to Redis...')
        await redis.set('test_connection', '1234')
        await redis.delete('test_connection')

    try:
        await _connect_to_redis()
    except RetryError:
        logger.error('Could not connect to Redis')
        raise


async def disconnect_redis() -> None:
    if config.TESTING:
        await redis.flushdb()
    await redis.close()
