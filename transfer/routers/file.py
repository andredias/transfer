from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, PlainTextResponse
from loguru import logger

from .. import config
from ..file_utils import remove_file_transfered, save_file
from ..resources import scheduler

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

    if not file.filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Missing filename')

    # save the file
    # Content-Length header is not reliable to prevent overflow
    # see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
    logger.info(f'Uploading file {file.filename}')
    try:
        token, filename = await save_file(file.filename, file)
    except OSError:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE) from None

    # schedule file removal
    scheduler.add_job(
        remove_file_transfered,
        'date',
        run_date=datetime.utcnow() + timedelta(seconds=config.TIMEOUT_INTERVAL),
        args=[token, filename],
    )

    # return the URL location of the file
    if request.headers.get('X-Forwarded-Proto'):  # served by a reverse proxy
        host = request.headers.get('X-Forwarded-Host') or request.headers.get('Host')
        location = urljoin(
            f'{request.headers["X-Forwarded-Proto"]}://{host}',
            f'{request.url.path}{router.prefix}{token}/{filename}',
        )
    else:  # served directly
        location = urljoin(request.url._url, f'{router.prefix}/{token}/{filename}')
    response.headers['Location'] = location
    return location


@router.get('/{token}/{filename}', status_code=status.HTTP_200_OK)
async def download_file(
    token: str,
    filename: str,
) -> FileResponse:
    """
    Download a file

    The token is the name of the directory where the file is stored.
    """
    paths = (
        Path('static', token, filename),
        Path(config.UPLOAD_DIR, token, filename),
    )
    for path in paths:
        if path.exists():
            logger.debug(f'Downloading file {path}')
            return FileResponse(path)
    raise HTTPException(status.HTTP_404_NOT_FOUND)


@router.delete('/{token}/{filename}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    token: str,
    filename: str,
) -> None:
    """
    Delete a file

    The token is the name of the directory where the file is stored.
    """
    try:
        remove_file_transfered(token, filename)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND) from None


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
