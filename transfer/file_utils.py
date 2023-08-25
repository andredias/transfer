import secrets
from shutil import rmtree
from time import time
from typing import Protocol

import aiofiles
from loguru import logger

from . import config


def remove_file_transfered(token: str, filename: str) -> None:
    """
    Remove a file and its parent directory
    """
    logger.info(f'Time out: Removing file {token}/{filename}')
    # since token is supposed to be unique, filename is not needed
    path = config.UPLOAD_DIR / token / filename
    if not path.exists():
        raise FileNotFoundError(f'File {token}/{filename} does not exist')
    rmtree(config.UPLOAD_DIR / token)


def timeout_job() -> None:
    """
    Remove files that have been stored for too long
    """
    timeout_ref = time() - config.TIMEOUT_INTERVAL
    for path in config.UPLOAD_DIR.glob('*/*'):
        if path.stat().st_mtime < timeout_ref:
            remove_file_transfered(*path.relative_to(config.UPLOAD_DIR).parts)


class Readable(Protocol):
    async def read(self, size: int) -> bytes:
        ...


async def save_file(filename: str, file: Readable) -> tuple[str, str]:
    """
    save the file
    Content-Length header is not reliable to prevent overflow
    see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
    """
    # TODO: sanitize filename
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
        remove_file_transfered(token, filename)
        raise OSError(f'File {filename} is too large')
    return token, filename
