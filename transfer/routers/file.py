import secrets
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

import aiofiles
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi_limiter.depends import RateLimiter
from loguru import logger

from .. import config
from ..file_utils import remove_file_and_parent
from ..resources import scheduler

router = APIRouter()


async def valid_content_length(content_length: int = Header(..., lt=config.FILE_SIZE_LIMIT)) -> int:
    return content_length


@router.post(
    '/',
    dependencies=[
        Depends(valid_content_length),
        Depends(RateLimiter(times=config.RATE_LIMIT_TIMES, seconds=config.RATE_LIMIT_SECONDS)),
    ],
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

    if not file.filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Missing filename')

    # save the file
    # Content-Length header is not reliable to prevent overflow
    # see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
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
        remove_file_and_parent(path)
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    # schedule file removal
    scheduler.add_job(
        remove_file_and_parent,
        'date',
        run_date=datetime.utcnow() + timedelta(seconds=config.TIMEOUT_INTERVAL),
        args=[path],
    )

    # return the URL location of the file
    if request.headers.get('X-Forwarded-Proto'):  # served by a reverse proxy
        location = urljoin(
            f'{request.headers["X-Forwarded-Proto"]}://{request.headers["X-Forwarded-Host"]}',
            f'{request.url.path}{router.prefix}{path.relative_to(config.UPLOAD_DIR)}',
        )
    else:  # served directly
        location = urljoin(
            request.url._url, f'{router.prefix}/{path.relative_to(config.UPLOAD_DIR)}'
        )
    response.headers['Location'] = location
    return location


@router.get('/{token}/{filename}', status_code=status.HTTP_200_OK)
async def download_file(
    token: str,
    filename: str,
    request: Request,
) -> FileResponse:
    """
    Download a file

    The token is the name of the directory where the file is stored.
    """
    if (
        request.headers.get('Sec-Fetch-Dest') or len(token) < config.TOKEN_LENGTH
    ):  # it came from a web page
        path = Path('static', token, filename)
    else:
        path = config.UPLOAD_DIR / token / filename
    logger.debug(f'Downloading file {path}')
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return FileResponse(path)


@router.delete('/{token}/{filename}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    token: str,
    filename: str,
) -> None:
    """
    Delete a file

    The token is the name of the directory where the file is stored.
    """
    path = config.UPLOAD_DIR / token / filename
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    remove_file_and_parent(path)
    return


# The next routes handle static content


@router.get('/', include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse('static/index.html')


@router.get('/{path:path}', include_in_schema=False)
async def serve_static_files(path: str) -> FileResponse:
    logger.debug(f'Getting static file {path}')
    filepath = Path('static', path)
    if not filepath.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return FileResponse(filepath)
