import secrets
from pathlib import Path
from typing import Final
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient

from transfer import config
from transfer.file_utils import file_exists
from transfer.resources import scheduler

SIZE_LIMIT: Final[int] = 10


@patch.dict(config.__dict__, {'FILE_SIZE_LIMIT': SIZE_LIMIT})
async def test_upload_file_over_size_limit(tmp_path: Path, client: AsyncClient) -> None:
    filename = tmp_path / 'over_sized.txt'
    filename.write_text(secrets.token_hex(SIZE_LIMIT + 1))
    resp = await client.post('/', files={'file': open(str(filename), 'rb')})
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    # try to cheat by setting the Content-Length header
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


async def test_file_lifecycle(tmp_path: Path, client: AsyncClient) -> None:
    # create a file
    hello_world = tmp_path / 'hello_world.txt'
    hello_world.write_text('hello world')

    # upload the file
    resp = await client.post('/', files={'file': open(str(hello_world), 'rb')})
    assert resp.status_code == status.HTTP_201_CREATED
    link = resp.headers['Location']
    token, filename = link.split('/')[-2:]
    assert link == resp.text == f'http://testserver/{token}/{filename}'
    assert file_exists(token, filename)
    job_id = f'{token}/{filename}'
    assert scheduler.get_job(job_id) is not None

    # upload the same file but faking a reverse proxy
    resp = await client.post(
        '/',
        files={'file': open(str(hello_world), 'rb')},
        headers={'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': 'transfer.pronus.io'},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    token2, filename2 = resp.text.split('/')[-2:]
    assert token != token2
    assert filename == filename2
    assert (
        resp.headers['Location'] == resp.text == f'https://transfer.pronus.io/{token2}/{filename2}'
    )

    # get existing file
    resp = await client.get(link)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.text == 'hello world'
    assert scheduler.get_job(job_id) is not None

    # delete file
    resp = await client.delete(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not file_exists(token, filename)
    assert scheduler.get_job(job_id) is None

    # get non-existing file
    resp = await client.get(link)
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # delete non-existing file
    resp = await client.delete(f'/{token}/{filename}')
    assert resp.status_code == status.HTTP_404_NOT_FOUND
