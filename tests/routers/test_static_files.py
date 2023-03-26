from typing import Final

from fastapi import status
from httpx import AsyncClient

KiB: Final[int] = 1024


async def test_index(client: AsyncClient) -> None:
    response = await client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert '<!doctype html>' in response.text


async def test_serve_static_files(client: AsyncClient) -> None:
    response = await client.get('/favicon.ico', headers={'Sec-Fetch-Dest': 'image'})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'image/vnd.microsoft.icon'
    assert response.content.startswith(b'\x00\x00\x01\x00')


async def test_serve_static_files_that_matches_download_file(client: AsyncClient) -> None:
    response = await client.get('/styles/main.css', headers={'Sec-Fetch-Dest': 'style'})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'text/css; charset=utf-8'
    assert int(response.headers['content-length']) > 1 * KiB

    # it should also work without the header
    response = await client.get('/styles/main.css')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'text/css; charset=utf-8'
    assert int(response.headers['content-length']) > 1 * KiB


async def test_get_static_files_with_invalid_path(client: AsyncClient) -> None:
    response = await client.get('/invalid')
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_static_files_with_longer_path_than_token(client: AsyncClient) -> None:
    response = await client.get('/fonts/font-awesome/fontawesome-webfont.svg')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'image/svg+xml'
    assert int(response.headers['content-length']) > 1 * KiB
