# orbitlab/adapters/base.pyi

from pathlib import Path
from typing import Any, Optional

class BaseProjectAdapter:
    """
    Permite herencia inversa desde proyectos externos, cargando sus settings
    desde un archivo global_imports.py.
    """
    settings: Any

    def __init__(self, custom_path: Optional[str] = ...) -> None: ...
    def _resolve_settings(self, custom_path: Optional[str] = ...) -> Any: ...
