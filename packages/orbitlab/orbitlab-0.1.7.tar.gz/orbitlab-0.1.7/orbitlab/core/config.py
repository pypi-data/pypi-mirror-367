from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class OrbitSettings(BaseSettings):
    PROJECT_NAME: str = "Orbit Lab"
    PUBLIC_KEY: Optional[str] = ""
    PRIVATE_KEY: Optional[str] = ""

    # Umbral global de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    # Habilitación y nivel mínimo por destino
    ENABLE_CONSOLE: bool = False
    CONSOLE_LEVEL:    Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    ENABLE_FILE:    bool = False
    FILE_LEVEL:     Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Ruta del archivo de logs
    LOG_FORMAT: Literal["text","json","csv"] = "text"
    LOGS_DIR: Optional[str] = "./logs/orbitlab.log"

    # Path para imports globales (opcional)
    GLOBAL_IMPORTS_PATH: Optional[str] = "global_imports.py"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia de configuración
settings = OrbitSettings()
