from pathlib import Path
from time import time
from unittest.mock import patch

import aiofiles
from pytest import raises

from transfer import config
from transfer.file_utils import file_exists, remove_expired_files, remove_file, save_file


async def test_remove_expired_files(tmp_path: Path) -> None:
    """
    Test removal of files that have been stored for too long
    """
    dummy = tmp_path / 'dummy.txt'
    dummy.write_text('dummy')
    async with aiofiles.open(dummy, 'rb') as file:
        token, filename = await save_file(file)
    assert file_exists(token, filename)

    # no expired files yet
    remove_expired_files()
    assert file_exists(token, filename)

    # fake a time in the  future...
    with patch('transfer.file_utils.time', return_value=time() + config.TIMEOUT_INTERVAL):
        remove_expired_files()
    assert not file_exists(token, filename)


async def test_file_cycle(tmp_path: Path) -> None:
    assert not file_exists('tralala', 'dummy.txt')

    dummy = tmp_path / 'dummy.txt'
    dummy.write_text('hello world')
    async with aiofiles.open(dummy, 'rb') as file:
        token, filename = await save_file(file)
    assert file_exists(token, filename)
    remove_file(token, filename)
    assert not file_exists(token, filename)


@patch.dict(config.__dict__, {'FILE_SIZE_LIMIT': 10})
async def test_file_overflow(tmp_path: Path) -> None:
    """
    Test that a file that is too large is not saved
    """
    filename = tmp_path / 'dummy.txt'
    filename.write_text('hello world')
    async with aiofiles.open(filename, 'rb') as file:
        with raises(OSError):
            await save_file(file)
