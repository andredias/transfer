from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse
from loguru import logger

from .. import config

router = APIRouter()


async def valid_content_length(content_length: int = Header(..., lt=config.FILE_SIZE_LIMIT)):
    return content_length


@router.post('/', dependencies=[Depends(valid_content_length)], response_class=PlainTextResponse)
async def upload_file(
    file: UploadFile,
) -> str:
    """
    Upload a file

    see: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
    """
    logger.info(f'Uploading file {file.filename}')
    path = config.UPLOAD_DIR / Path(file.filename).name
    real_file_size = 0
    try:
        async with aiofiles.open(str(path), 'wb') as out_file:
            while content := await file.read(config.BUFFER_SIZE):  # async read chunk
                real_file_size += len(content)
                if real_file_size > config.FILE_SIZE_LIMIT:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f'file size is greater than {config.FILE_SIZE_LIMIT} bytes',
                    )
                await out_file.write(content)  # async write chunk
    except OSError:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR) from None

    return f'File {file.filename} uploaded successfully'
