import secrets
from pathlib import Path
from typing import Final
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient

from transfer import config
from transfer.resources import scheduler

SIZE_LIMIT: Final[int] = 2**10  # 1KiB


async def test_upload_file_ok_local(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'dummy.txt'
    filename.write_text('hello world')
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    with patch('transfer.file_utils.secrets.token_urlsafe', return_value=token):
        resp = await client.post('/', files={'file': open(str(filename), 'rb')})
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.headers['Location'] == resp.text == f'http://testserver/{token}/{filename.name}'
    path = Path(config.UPLOAD_DIR / token / filename.name)
    assert path.read_text() == 'hello world'


async def test_upload_file_ok_proxy_server(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'hello.txt'
    filename.write_text('hello world')
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    with patch('transfer.file_utils.secrets.token_urlsafe', return_value=token):
        resp = await client.post(
            '/',
            files={'file': open(str(filename), 'rb')},
            headers={'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': 'transfer.pronus.io'},
        )
    assert resp.status_code == status.HTTP_201_CREATED
    assert (
        resp.headers['Location']
        == resp.text
        == f'https://transfer.pronus.io/{token}/{filename.name}'
    )
    path = Path(config.UPLOAD_DIR / token / filename.name)
    assert path.read_text() == 'hello world'


@patch.dict(config.__dict__, {'FILE_SIZE_LIMIT': SIZE_LIMIT})
async def test_upload_file_over_size_limit(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'over_sized.txt'
    filename.write_text(secrets.token_hex(SIZE_LIMIT + 1))
    resp = await client.post('/', files={'file': open(str(filename), 'rb')})
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    # try to cheat by setting Content-Length header
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    with patch('transfer.file_utils.secrets.token_urlsafe', return_value=token):
        resp = await client.post(
            '/',
            files={'file': open(str(filename), 'rb')},
            headers={'Content-Length': str(SIZE_LIMIT // 2)},
        )
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    path = config.UPLOAD_DIR / token / filename.name
    assert not path.exists()
    assert not path.parent.exists()


async def test_download_existing_file(client: AsyncClient) -> None:
    filename = 'tralala.txt'
    content = 'Hello world'
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    path = config.UPLOAD_DIR / token / filename
    path.parent.mkdir()
    path.write_text(content)
    resp = await client.get(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.text == content


async def test_download_non_existing_file(client: AsyncClient) -> None:
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    filename = 'non_existing.txt'
    resp = await client.get(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_existing_file(client: AsyncClient) -> None:
    filename = 'tralala.txt'
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    path = config.UPLOAD_DIR / token / filename
    path.parent.mkdir()
    path.write_text('Hello world')
    resp = await client.delete(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not path.exists()
    assert not path.parent.exists()


async def test_delete_non_existing_file(client: AsyncClient) -> None:
    filename = 'non_existing.txt'
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    resp = await client.delete(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_job_removal_after_manual_deletion(tmp_path: Path, client: AsyncClient) -> None:
    filepath = tmp_path / 'dummy.txt'
    filepath.write_text('hello world')
    resp = await client.post('/', files={'file': open(str(filepath), 'rb')})
    assert resp.status_code == status.HTTP_201_CREATED
    link = resp.headers['Location']
    token, filename = link.split('/')[-2:]
    job_id = f'{token}/{filename}'
    assert scheduler.get_job(job_id) is not None

    resp = await client.delete(link)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert scheduler.get_job(job_id) is None
