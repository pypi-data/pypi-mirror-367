import os
import sys
import json
import logging
import structlog
from logging import Logger, NullHandler, FileHandler, LogRecord
from structlog.typing import EventDict

from orbitlab.core.config import settings

# Formato de timestamp
TIMESTAMP_FMT = "%I:%M:%S %p %d/%m/%Y"


def clean_log_level(
    logger: Logger,
    name: str,
    event_dict: EventDict,
    is_console: bool = False,
) -> EventDict:
    level = event_dict.get("level", "").upper().strip()
    if is_console:
        colors = {
            "DEBUG": "\033[1;32mDEBUG\033[0m",
            "INFO": "\033[0;36mINFO\033[0m",
            "WARNING": "\033[1;33mWARNING\033[0m",
            "ERROR": "\033[1;31mERROR\033[0m",
            "CRITICAL": "\033[1;35mCRITICAL\033[0m",
        }
        level = colors.get(level, level)
    else:
        level = f"[{level}]"
    event_dict["level"] = level
    return event_dict


def format_timestamp(
    logger: Logger,
    name: str,
    event_dict: EventDict,
) -> EventDict:
    ts = event_dict.get("timestamp", "")
    if ts:
        event_dict["timestamp"] = ts.strip()
    return event_dict


def text_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict,
) -> str:
    """
    Legacy text: línea legible + UNA sola coma final.
    """
    ts    = event_dict.pop("timestamp", "")
    lvl   = event_dict.pop("level", "")
    ev    = event_dict.pop("event", "")
    extra = " ".join(f"{k}={v}" for k, v in event_dict.items())
    line  = f"{ts} {lvl} {ev} {extra}".strip()
    return line + ","


def json_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict,
) -> str:
    """
    Un objeto JSON por línea (NDJSON), sin coma final.
    """
    return json.dumps(event_dict, ensure_ascii=False)


def csv_renderer(
    logger: Logger,
    name: str,
    event_dict: EventDict,
) -> str:
    """
    CSV con columnas:
      "timestamp","level","event","filepath"
    Todas entre comillas, sin coma final.
    Extrae filepath del final del mensaje (después de 'Archivo:').
    """
    d        = dict(event_dict)
    ts       = d.get("timestamp", "")
    lvl      = d.get("level", "").strip("[]")
    ev_raw   = d.get("event", "")

    filepath = ""
    if "Archivo:" in ev_raw:
        before, after = ev_raw.split("Archivo:", 1)
        ev_msg   = before.split("||", 1)[0].strip().rstrip(",")
        filepath = after.strip().rstrip(",")
    else:
        ev_msg = ev_raw

    # Función para quotear campos CSV
    def quote(s: str) -> str:
        s2 = s.replace('"', '""')
        return f'"{s2}"'

    return ",".join([
        quote(ts),
        quote(lvl),
        quote(ev_msg),
        quote(filepath),
    ])



class JsonArrayFileHandler(FileHandler):
    """
    FileHandler que mantiene un único array JSON:
    - Si el archivo NO existe: crea y escribe "[\n".
    - Si YA existe: lo abre con 'a', pero antes elimina el ']' final.
    Luego, en cada emit, inserta la coma necesaria para separar objetos,
    y finalmente en close() añade "\n]\n".
    """
    def __init__(self, filename: str, encoding: str = "utf-8"):
        if os.path.exists(filename):
            with open(filename, "rb+") as f:
                f.seek(0, os.SEEK_END)
                pos = f.tell() - 1
                while pos > 0:
                    f.seek(pos)
                    if f.read(1) == b"]":
                        f.truncate(pos)
                        break
                    pos -= 1
            mode = "a"
            self.first = False
        else:
            mode = "w"
            self.first = True

        super().__init__(filename, mode=mode, encoding=encoding)
        if self.first:
            self.stream.write("[\n")

    def emit(self, record: LogRecord) -> None:
        try:
            msg = self.format(record)
            if not self.first:
                self.stream.write(",\n")
            else:
                self.first = False
            self.stream.write(msg)
            self.stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        if hasattr(self, "stream") and not self.stream.closed:
            # Cerramos el array JSON
            self.stream.write("\n]\n")
        super().close()


# ————————————————————————————————————————————————
# CONFIGURACIÓN DEL LOGGER RAÍZ
# ————————————————————————————————————————————————

logger: Logger = logging.getLogger()
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger.handlers.clear()
logger.addHandler(NullHandler())

if settings.ENABLE_CONSOLE:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.CONSOLE_LEVEL, logging.INFO))
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=[
                structlog.processors.TimeStamper(fmt=TIMESTAMP_FMT, utc=False, key="timestamp"),
                format_timestamp,
                structlog.processors.add_log_level,
                lambda l, n, e: clean_log_level(l, n, e, is_console=True),
            ],
        )
    )
    logger.addHandler(console_handler)

# Archivo con formato dinámico
if settings.ENABLE_FILE and settings.LOGS_DIR:
    os.makedirs(os.path.dirname(settings.LOGS_DIR), exist_ok=True)

    fmt = getattr(settings, "LOG_FORMAT", None)
    if fmt == "json":
        file_handler = JsonArrayFileHandler(settings.LOGS_DIR, encoding="utf-8")
    else:
        # csv y text usan handler estándar
        file_handler = FileHandler(settings.LOGS_DIR, encoding="utf-8")

    file_handler.setLevel(getattr(logging, settings.FILE_LEVEL, logging.ERROR))

    if fmt == "json":
        renderer = json_renderer
    elif fmt == "csv":
        renderer = csv_renderer
    else:
        renderer = text_renderer

    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=[
                structlog.processors.TimeStamper(fmt=TIMESTAMP_FMT, utc=False, key="timestamp"),
                format_timestamp,
                structlog.processors.add_log_level,
                lambda l, n, e: clean_log_level(l, n, e, is_console=False),
            ],
        )
    )
    logger.addHandler(file_handler)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt=TIMESTAMP_FMT, utc=False, key="timestamp"),
        format_timestamp,
        structlog.processors.add_log_level,
        lambda l, n, e: clean_log_level(l, n, e, is_console=False),
        structlog.processors.CallsiteParameterAdder([
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
        ]),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
