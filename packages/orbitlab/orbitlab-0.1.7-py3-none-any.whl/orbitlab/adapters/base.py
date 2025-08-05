# orbitlab/adapters/base.py
import sys
import importlib.util
from pathlib import Path
from typing import Any, Optional
import os

class BaseProjectAdapter:
    """
    Permite herencia inversa desde proyectos externos, cargando sus settings desde un archivo global_imports.py.
    Soporta ubicación dinámica del archivo mediante variable de entorno GLOBAL_IMPORTS_PATH o ruta por defecto.
    """

    def __init__(self, custom_path: Optional[str] = None) -> None:
        self.settings = self._resolve_settings(custom_path)

    def _resolve_settings(self, custom_path: Optional[str]) -> Any:
        env_path = os.getenv("GLOBAL_IMPORTS_PATH")
        base_path = Path(env_path or custom_path or Path.cwd() / "global_imports.py")

        if base_path.exists():
            spec = importlib.util.spec_from_file_location("global_imports", str(base_path))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["global_imports"] = module
                spec.loader.exec_module(module)
                return getattr(module, "settings", {}) 

        return {} 
