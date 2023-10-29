import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

ENV: str = os.getenv('ENV', 'production').lower()
if ENV not in ('production', 'development', 'testing'):
    raise ValueError(
        f'ENV={ENV} is not valid. ' "It should be 'production', 'development' or 'testing'"
    )
DEBUG: bool = ENV != 'production'
TESTING: bool = ENV == 'testing'

os.environ['LOGURU_LEVEL'] = os.getenv('LOG_LEVEL') or (DEBUG and 'DEBUG') or 'INFO'
os.environ['LOGURU_DEBUG_COLOR'] = '<fg #777>'
REQUEST_ID_LENGTH = int(os.getenv('REQUEST_ID_LENGTH', '8'))
PYGMENTS_STYLE = os.getenv('PYGMENTS_STYLE', 'github-dark')

MiB: Final[int] = 2**20

BUFFER_SIZE: int = int(os.getenv('BUFFER_SIZE') or 1 * MiB)
FILE_SIZE_LIMIT: int = int(os.getenv('FILE_SIZE_LIMIT') or 5 * MiB)
UPLOAD_DIR: Path = Path(os.getenv('UPLOAD_DIR', '/tmp/transfer_files'))  # noqa: S108
TOKEN_LENGTH: int = int(os.getenv('TOKEN_LENGTH') or 8)
TIMEOUT_INTERVAL: int = int(os.getenv('TIMEOUT_INTERVAL_MIN') or 3_600)  # in seconds
