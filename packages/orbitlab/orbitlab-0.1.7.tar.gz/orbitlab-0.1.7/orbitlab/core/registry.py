# orbitlab/core/registry.py

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from orbitlab.core.utils import log_message

class OrbitRegistry:
    """
    Registro local de versiones de archivos .dill.
    Guarda metadatos como autor, tags, timestamp y hash único.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.data: Dict[str, Dict[str, Any]] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text(encoding="utf-8"))
            except Exception as e:
                log_message("Error al cargar registro", level="error", error=str(e))
                return {}
        return {}

    def _save_registry(self) -> None:
        try:
            self.registry_path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            log_message("Error al guardar el registro", level="error", error=str(e))

    def _hash_file(self, path: Path) -> str:
        return hashlib.blake2b(path.read_bytes()).hexdigest()

    def register(
        self,
        dill_file: Path,
        author: str = "anon",
        tags: Optional[List[str]] = None,
        description: str = ""
    ) -> Tuple[str, Dict[str, Any]]:
        if not dill_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {dill_file}")

        dill_hash = self._hash_file(dill_file)
        version_key = f"{dill_file.name}:{dill_hash[:8]}"

        entry: Dict[str, Any] = {
            "file": dill_file.name,
            "hash": f"blake2b:{dill_hash}",
            "author": author,
            "tags": tags or [],
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.data[version_key] = entry
        self._save_registry()
        log_message(f"Dill registrado como {version_key}", emoji="📘")
        return version_key, entry

    def list_versions(self, file_name: str) -> Dict[str, Dict[str, Any]]:
        return {
            key: value
            for key, value in self.data.items()
            if key.startswith(f"{file_name}:")
        }

    def get_entry(self, version_key: str) -> Optional[Dict[str, Any]]:
        return self.data.get(version_key)

    def remove_entry(self, version_key: str) -> bool:
        if version_key in self.data:
            del self.data[version_key]
            self._save_registry()
            log_message(f"Entrada eliminada: {version_key}", emoji="🗑️", level="info")
            return True
        log_message(f"No se encontró la entrada: {version_key}", level="warning")
        return False

__all__ = ["OrbitRegistry"]
