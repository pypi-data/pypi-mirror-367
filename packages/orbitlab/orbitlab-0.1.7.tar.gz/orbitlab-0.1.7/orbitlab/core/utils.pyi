# orbitlab/core/utils.pyi

from typing import Any, Optional, Literal
from pathlib import Path

LogLevel = Literal["info", "debug", "warning", "error", "critical"]

class ScopedAtomicCounter:
    def __init__(self) -> None: ...
    def increment(self, scope: str = ...) -> int: ...

counter: ScopedAtomicCounter

def log_message(
    message: Optional[str] = ...,
    emoji: str = ...,
    scope: str = ...,
    level: LogLevel = ...,
    **variables: Any
) -> None: ...
