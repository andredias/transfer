from pathlib import Path
from shutil import rmtree
from time import time

from loguru import logger

from . import config


def remove_file_and_parent(path: Path) -> None:
    """
    Remove a file and its parent directory
    """
    logger.info(f'Time out: Removing file {path}')
    rmtree(path.parent)


def timeout_job() -> None:
    """
    Remove files that have been stored for too long
    """
    timeout_ref = time() - config.TIMEOUT_INTERVAL
    for path in config.UPLOAD_DIR.glob('*/*'):
        if path.stat().st_mtime < timeout_ref:
            remove_file_and_parent(path)
