import secrets
from time import time
from unittest.mock import patch

from transfer import config
from transfer.file_utils import remove_file_transfered, timeout_job


def test_remove_file() -> None:
    """
    Test that remove_file() removes a file and its parent directory
    """
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    filename = 'dummy.txt'
    path = config.UPLOAD_DIR / token / filename
    path.parent.mkdir(parents=True)
    path.write_text('dummy')
    assert path.exists()
    remove_file_transfered(token, filename)
    assert not path.exists()
    assert not path.parent.exists()


def test_timeout_job() -> None:
    """
    Test that timeout_job() removes files that have been stored for too long
    """
    token = secrets.token_urlsafe(config.TOKEN_LENGTH)
    path = config.UPLOAD_DIR / token / 'dummy.txt'
    path.parent.mkdir(parents=True)
    path.write_text('dummy')

    timeout_job()
    assert path.exists()

    # move to the future...
    with patch('transfer.file_utils.time', return_value=time() + config.TIMEOUT_INTERVAL):
        timeout_job()
    assert not path.exists()
    assert not path.parent.exists()
