from fastapi import APIRouter
from loguru import logger

router = APIRouter()


@router.get('/hello', include_in_schema=False)
async def hello_world() -> dict[str, str]:
    logger.info('Hello world!')
    return {'message': 'Hello World'}
