# orbitlab/core/cache.py
import dill  # type: ignore
import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict, cast
from orbitlab.core.crypto import firmar_dill
from orbitlab.core.utils import log_message


class OrbitCache:
    """
    Sistema de caché para objetos serializados con dill.
    Soporta validación opcional por hash y limpieza selectiva.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, identifier: str) -> str:
        return hashlib.blake2b(identifier.encode(), digest_size=16).hexdigest()

    def _get_cache_file(self, identifier: str) -> Path:
        cache_key = self._generate_cache_key(identifier)
        return self.cache_dir / f"{cache_key}.dill"

    def get(self, identifier: str, validate_hash: bool = False) -> Optional[Dict[str, Any]]:
        cache_file = self._get_cache_file(identifier)
        sig_file = cache_file.with_suffix(".dill.sig")

        if not cache_file.exists():
            return None

        try:
            with cache_file.open("rb") as f:
                obj = cast(Dict[str, Any], dill.load(f))  # type: ignore

            if validate_hash:
                if sig_file.exists():
                    expected = json.loads(sig_file.read_text(encoding="utf-8"))
                    actual = self._calculate_hash(cache_file.read_bytes())
                    sig_hash = expected.get("hash", "").split(":")[-1]
                    if actual != sig_hash:
                        log_message(f"Firma inválida para {cache_file.name}. Se ignora caché.", level="warning")
                        return None
                else:
                    log_message(f"No se encontró firma para validar caché: {cache_file.name}", level="warning")
                    return None

            return obj
        except Exception as e:
            log_message(f"Error al leer caché: {e}", level="error")
            return None

    def set(self, identifier: str, obj: Dict[str, Any]) -> None:
        cache_file = self._get_cache_file(identifier)
        try:
            obj["__cache_hash__"] = self._calculate_hash(dill.dumps(obj))  # type: ignore
            with cache_file.open("wb") as f:
                dill.dump(obj, f)  # type: ignore
            firmar_dill(cache_file)
        except Exception as e:
            log_message(f"Error al guardar caché: {e}", level="error")

    def clear(self) -> None:
        count = 0
        for file in self.cache_dir.glob("*.dill"):
            file.unlink()
            count += 1
        log_message(f"Caché limpiado. Archivos eliminados: {count}", emoji="🧹", level="info")

    def remove(self, identifier: str) -> bool:
        cache_file = self._get_cache_file(identifier)
        if cache_file.exists():
            cache_file.unlink()
            log_message(f"Entrada de caché eliminada: {cache_file.name}", emoji="🗑️", level="info")
            return True
        return False

    def _calculate_hash(self, data: bytes) -> str:
        return hashlib.blake2b(data).hexdigest()
