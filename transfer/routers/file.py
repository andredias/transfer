import secrets
from pathlib import Path
from urllib.parse import urljoin

import aiofiles
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import PlainTextResponse
from loguru import logger

from .. import config

router = APIRouter()


async def valid_content_length(content_length: int = Header(..., lt=config.FILE_SIZE_LIMIT)) -> int:
    return content_length


@router.post(
    '/',
    dependencies=[Depends(valid_content_length)],
    response_class=PlainTextResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile,
    request: Request,
    response: Response,
) -> str:
    """
    Upload a file

    1. In order to prevent name collision, the file is saved in a directory with a random name.
    2. The path to the file is returned as plain text but also set as the Location header.
    """
    # Content-Length header is not reliable to prevent overflow
    # see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025

    if not file.filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Missing filename')
    logger.info(f'Uploading file {file.filename}')
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    path = config.UPLOAD_DIR / token / Path(file.filename).name
    real_file_size = 0
    overflow = False
    path.parent.mkdir()
    async with aiofiles.open(path, 'wb') as out_file:
        while content := await file.read(config.BUFFER_SIZE):
            real_file_size += len(content)
            if overflow := real_file_size > config.FILE_SIZE_LIMIT:
                break
            await out_file.write(content)
    if overflow:
        path.unlink()
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    location = urljoin(request.url._url, f'{router.prefix}/{path.relative_to(config.UPLOAD_DIR)}')
    response.headers['Location'] = location
    return location
