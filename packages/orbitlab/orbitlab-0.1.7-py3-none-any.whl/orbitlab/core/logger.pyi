# orbitlab/core/logger.pyi

from logging import Logger, LogRecord, StreamHandler, FileHandler
from structlog.typing import EventDict
from typing import Optional, Callable

TIMESTAMP_FMT: str

def clean_log_level(
    logger: Logger,
    name: str,
    event_dict: EventDict,
    is_console: bool = ...
) -> EventDict: ...

def format_timestamp(
    logger: Logger,
    name: str,
    event_dict: EventDict
) -> EventDict: ...

def text_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict
) -> str: ...

def json_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict
) -> str: ...

def csv_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict
) -> str: ...

class JsonArrayFileHandler(FileHandler):
    first: bool
    def __init__(self, filename: str, encoding: str = ...) -> None: ...
    def emit(self, record: LogRecord) -> None: ...
    def close(self) -> None: ...

logger: Logger
console_handler: Optional[StreamHandler]
file_handler: Optional[FileHandler]
renderer: Callable[[Logger, str, EventDict], str]
