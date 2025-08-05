# orbitlab/core/config.pyi

from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class OrbitSettings(BaseSettings):
    PROJECT_NAME: str
    PUBLIC_KEY: Optional[str]
    PRIVATE_KEY: Optional[str]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    ENABLE_CONSOLE: bool
    CONSOLE_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    ENABLE_FILE: bool
    FILE_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    LOG_FORMAT: Literal["text", "json", "csv"]
    LOGS_DIR: Optional[str]
    GLOBAL_IMPORTS_PATH: Optional[str]
    model_config: SettingsConfigDict

settings: OrbitSettings
