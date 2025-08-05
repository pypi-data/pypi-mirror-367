from __future__ import annotations
import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional, TypedDict, TypeVar, Union
import dill  # type: ignore
from filelock import FileLock

from orbitlab.core.crypto import firmar_dill, validar_firma, encrypt_hybrid, decrypt_hybrid
from orbitlab.core.utils import log_message

# ------------------- TrackedDictState -------------------
class TrackedDictState(TypedDict, total=False):
    _data: dict[Any, Any]
    _key: Any

# ------------------- TrackedDict -------------------
class TrackedDict(dict[Any, Any]):
    _parent: Optional[DynamicDillStore]
    _key: Any

    """
    Diccionario que notifica a su padre en cada cambio,
    soporta auto-guardado y auto-commit.
    """
    def __init__(
        self,
        parent: Optional[DynamicDillStore] = None,
        key: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._key = key

    def __setitem__(self, k: Any, v: Any) -> None:
        if isinstance(v, dict) and not isinstance(v, TrackedDict):
            v = TrackedDict(self._parent, self._key, v)
        super().__setitem__(k, v)
        self._trigger()

    def __delitem__(self, k: Any) -> None:
        super().__delitem__(k)
        self._trigger()

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self._trigger()

    def _trigger(self) -> None:
        parent = getattr(self, "_parent", None)
        key = getattr(self, "_key", None)
        if parent is not None and key is not None:
            parent._store[key] = self
            if getattr(parent, "auto_save", False):
                parent._save()
            if hasattr(parent, "_auto_commit_if_needed"):
                parent._auto_commit_if_needed(key)

    def __getstate__(self) -> TrackedDictState:
        return {"_data": dict(self), "_key": self._key}

    def __setstate__(self, state: TrackedDictState) -> None:
        if "_data" in state:
            dict.update(self, state["_data"])  # type: ignore
        self._key = state.get("_key", None)
        self._parent = None

    def __repr__(self) -> str:
        return f"TrackedDict({dict.__repr__(self)})"  # type: ignore

# ------------------- Alias para tipos en el store -------------------
StoreValue = Union[
    int,
    float,
    str,
    bool,
    dict[str, Any],
    TrackedDict,
]

# Función para convertir TrackedDict (y dict anidados) a dict puro
K = TypeVar('K')
V = TypeVar('V')
T = TypeVar('T')

def to_plain_dict(d: Union[TrackedDict, dict[Any, Any], T]) -> Union[dict[Any, Any], T]:
    if isinstance(d, dict):
        result: dict[Any, Any] = {}
        for k, v in d.items(): # type: ignore
            result[k] = to_plain_dict(v) # type: ignore
        return result
    return d

# ------------------- DynamicDillStore -------------------
class DynamicDillStore:
    def __init__(
        self,
        path: str,
        auto_reload: bool = True,
        auto_save: bool = True,
        auto_commit_interval: Optional[float] = None,
        secure: bool = False,
    ) -> None:
        self.path: str = path
        self.lock = FileLock(f"{self.path}.lock")
        self.auto_reload = auto_reload
        self.auto_save = auto_save
        self.auto_commit_interval = auto_commit_interval
        self.secure = secure

        self._last_commit_times: dict[str, float] = {}
        self._last_mtime: Optional[float] = None
        self._store: dict[str, StoreValue] = {}
        self._versions_path = f"{self.path}.versions"
        os.makedirs(self._versions_path, exist_ok=True)


        if os.path.exists(self.path):
            self._reload()
        else:
            self._save()

        if self.auto_save:
            try:
                import atexit
                atexit.register(self._save)
            except Exception:
                pass

    def _wrap_nested_dicts(self, data: Any, key: str) -> Any:
        if isinstance(data, dict) and not isinstance(data, TrackedDict):
            td = TrackedDict(self, key)
            for k2, v2 in data.items(): # type: ignore
                td[k2] = self._wrap_nested_dicts(v2, key)
            return td
        return data

    def _reattach_tracked_dicts(self) -> None:
        for k, v in list(self._store.items()):
            self._store[k] = self._wrap_nested_dicts(v, k)

    def _reload(self) -> None:
        try:
            if not os.path.exists(self.path):
                return
            mtime = os.path.getmtime(self.path)
            if self._last_mtime is None or mtime > self._last_mtime:
                with self.lock:
                    with open(self.path, 'rb') as f:
                        contenido = dill.load(f) # pyright: ignore[reportUnknownMemberType]
                        if (
                            isinstance(contenido, dict)
                            and contenido.get('secure') # pyright: ignore[reportUnknownMemberType]
                            and 'encrypted' in contenido
                        ):
                            self._store = decrypt_hybrid(contenido['encrypted'])  # type: ignore
                        else:
                            self._store = contenido
                self._last_mtime = mtime
                self._reattach_tracked_dicts()
        except Exception as e:
            log_message(f"[DynamicDillStore] Reload error: {e}", level='error')

    def _save(self) -> None:
        try:
            with self.lock:
                with open(self.path, 'wb') as f:
                    if self.secure:
                        encrypted = encrypt_hybrid(self._store)  # type: ignore
                        dill.dump({'secure': True, 'encrypted': encrypted}, f)  # type: ignore
                    else:
                        dill.dump(self._store, f)  # type: ignore
                self._last_mtime = os.path.getmtime(self.path)
        except Exception as e:
            log_message(f"[DynamicDillStore] Save error: {e}", level='error')

    def _auto_commit_if_needed(self, key: str) -> None:
        if self.auto_commit_interval is None:
            return
        now = time.time()
        last = self._last_commit_times.get(key, 0)
        if now - last >= self.auto_commit_interval:
            self.commit(key)

    def set(self, key: str, value: Any) -> None:
        if self.auto_reload:
            self._reload()
        wrapped = self._wrap_nested_dicts(value, key)
        with self.lock:
            self._store[key] = wrapped
            if self.auto_save:
                self._save()
            self._auto_commit_if_needed(key)

    def get(self, key: str, default: Any = None) -> Any:
        if self.auto_reload:
            self._reload()
        with self.lock:
            val = self._store.get(key, default)
            wrapped = self._wrap_nested_dicts(val, key)
            self._store[key] = wrapped
            return wrapped

    def delete(self, key: str) -> None:
        if self.auto_reload:
            self._reload()
        with self.lock:
            if key in self._store:
                del self._store[key]
                if self.auto_save:
                    self._save()

    def keys(self) -> list[str]:
        if self.auto_reload:
            self._reload()
        with self.lock:
            return list(self._store.keys())

    def values(self) -> list[Any]:
        if self.auto_reload:
            self._reload()
        with self.lock:
            return list(self._store.values())

    def items(self) -> list[tuple[str, Any]]:
        if self.auto_reload:
            self._reload()
        with self.lock:
            return list(self._store.items())

    def clear(self) -> None:
        with self.lock:
            self._store.clear()
            if self.auto_save:
                self._save()

    def commit(self, key: str) -> None:
        if key not in self._store:
            raise KeyError(f"Key '{key}' not found for commit")
        ts = time.strftime("%Y%m%d-%H%M%S")
        uid = uuid.uuid4().hex[:6]
        version_file = os.path.join(self._versions_path, f"{key}@{ts}_{uid}.dill")
        with open(version_file, 'wb') as f:
            dill.dump(self._store[key], f)  # type: ignore
        firmar_dill(Path(version_file))
        self._last_commit_times[key] = time.time()

    def history(self, key: str) -> list[str]:
        prefix = f"{key}@"
        return sorted(
            f.split("@", 1)[-1].replace('.dill', '')
            for f in os.listdir(self._versions_path)
            if f.startswith(prefix) and f.endswith('.dill')
        )

    def rollback(self, key: str, timestamp: str) -> None:
        matches = [f for f in os.listdir(self._versions_path) if f.startswith(f"{key}@{timestamp}") and f.endswith('.dill')]
        if not matches:
            raise FileNotFoundError(f"No version found for '{key}' at {timestamp}")
        version_file = os.path.join(self._versions_path, matches[0])
        if not validar_firma(Path(version_file)):
            raise ValueError(f"Firma inválida para la versión {matches[0]}")
        with open(version_file, 'rb') as f:
            value = dill.load(f) # type: ignore
        self.set(key, value)

    def __repr__(self) -> str:
        return f"<DynamicDillStore path={self.path} keys={list(self._store.keys())}>"
