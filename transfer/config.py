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

MiB: Final[int] = 2**20

BUFFER_SIZE: int = int(os.environ['BUFFER_SIZE']) if 'BUFFER_SIZE' in os.environ else 1 * MiB
FILE_SIZE_LIMIT: int = (
    int(os.environ['FILE_SIZE_LIMIT']) if 'FILE_SIZE_LIMIT' in os.environ else 5 * MiB
)
UPLOAD_DIR: Path = Path(os.getenv('UPLOAD_DIR', '/tmp/transfer_files'))  # noqa: S108
TOKEN_LENGTH: int = int(os.environ['TOKEN_LENGTH']) if 'TOKEN_LENGTH' in os.environ else 8
TIMEOUT_INTERVAL: int = (
    int(os.environ['TIMEOUT_INTERVAL_MIN']) if 'TIMEOUT_INTERVAL_MIN' in os.environ else 3_600
)  # in seconds

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = os.getenv('REDIS_URL') or f'redis://{REDIS_HOST}:{REDIS_PORT}'
