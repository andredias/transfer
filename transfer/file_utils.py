import secrets
from shutil import rmtree
from time import time
from typing import Protocol

import aiofiles
from loguru import logger

from . import config


def file_exists(token: str, filename: str) -> bool:
    return (config.UPLOAD_DIR / token / filename).exists()


def remove_file(token: str, filename: str) -> None:
    """
    Remove a file and its parent directory
    """
    rmtree(config.UPLOAD_DIR / token)


def remove_expired_files() -> None:
    """
    Remove files that have been stored for too long
    """
    timeout_ref = time() - config.TIMEOUT_INTERVAL
    for path in config.UPLOAD_DIR.glob('*/*'):
        if path.stat().st_mtime < timeout_ref:
            remove_file(*path.relative_to(config.UPLOAD_DIR).parts)


class Readable(Protocol):
    """
    It makes easier to mock the aiofiles stream during tests
    """

    async def read(self, size: int) -> bytes:
        ...


async def save_file(filename: str, file: Readable) -> tuple[str, str]:
    """
    save the file
    Content-Length header is not reliable to prevent overflow
    see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
    """
    logger.info(f'Uploading file {filename}')
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    path = config.UPLOAD_DIR / token / filename
    real_file_size = 0
    overflow = False
    path.parent.mkdir(parents=True)
    async with aiofiles.open(path, 'wb') as out_file:
        while content := await file.read(config.BUFFER_SIZE):
            real_file_size += len(content)
            if overflow := real_file_size > config.FILE_SIZE_LIMIT:
                break
            await out_file.write(content)
    if overflow:
        remove_file(token, filename)
        raise OSError(f'File {filename} is too large')
    return token, filename
