# orbitlab/core/utils.py

import inspect
from pathlib import Path
from threading import RLock
from collections import defaultdict
from typing import Any, Optional, Literal, Dict

from orbitlab.core.logger import logger

LogLevel = Literal["info", "debug", "warning", "error", "critical"]

class ScopedAtomicCounter:
    def __init__(self) -> None:
        self._lock: RLock = RLock()
        self._counters: Dict[str, int] = defaultdict(int)

    def increment(self, scope: str = "global") -> int:
        with self._lock:
            self._counters[scope] += 1
            return self._counters[scope]

counter = ScopedAtomicCounter()

def log_message(
    message: Optional[str] = None,
    emoji: str = "🛰️",
    scope: str = "orbit",
    level: LogLevel = "info",
    **variables: Any
) -> None:
    """
    Loggea un mensaje con contexto (línea, archivo, contador).
    Usa el logger configurado en orbitlab/core/logger.py.
    """
    count = counter.increment(scope)
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    line = caller.f_lineno if caller is not None else "?"
    file_path = Path(caller.f_code.co_filename).resolve() if caller is not None else Path("?")
    try:
        relative_path = file_path.relative_to(Path.cwd().resolve())
    except ValueError:
        relative_path = file_path
    path_str = str(relative_path)
    header = f"{emoji} {count} [{scope}]"
    details = f" || Línea: {line}, Archivo: {path_str}"
    vars_str = " ".join(f"{k}={v}" for k, v in variables.items())
    full_message = f"{header} {message or ''}{details} {vars_str}".strip()
    log_fn = getattr(logger, level, logger.info)
    log_fn(full_message)
