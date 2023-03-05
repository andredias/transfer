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

LOG_LEVEL: str = os.getenv('LOG_LEVEL') or (DEBUG and 'DEBUG') or 'INFO'
os.environ['LOGURU_DEBUG_COLOR'] = '<fg #777>'

MiB: Final[int] = 2**20

BUFFER_SIZE: int = int(os.getenv('BUFFER_SIZE', 1 * MiB))
FILE_SIZE_LIMIT: int = int(os.getenv('FILE_SIZE_LIMIT', 5 * MiB))
UPLOAD_DIR: Path = Path(os.getenv('UPLOAD_DIR', '/dev/shm'))
