import secrets
from pathlib import Path
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient

from transfer import config

SIZE_LIMIT = 2**10


async def test_upload_file_ok(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'dummy.txt'
    filename.write_text('hello world')
    resp = await client.post('/', files={'file': open(str(filename), 'rb')})
    assert resp.status_code == status.HTTP_200_OK


@patch.dict(config.__dict__, {'FILE_SIZE_LIMIT': SIZE_LIMIT})
async def test_upload_file_over_size_limit(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'over_sized.txt'
    filename.write_text(secrets.token_hex(SIZE_LIMIT + 1))
    resp = await client.post('/', files={'file': open(str(filename), 'rb')})
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    # try to cheat by setting Content-Length header
    resp = await client.post(
        '/',
        files={'file': open(str(filename), 'rb')},
        headers={'Content-Length': str(SIZE_LIMIT // 2)},
    )
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
