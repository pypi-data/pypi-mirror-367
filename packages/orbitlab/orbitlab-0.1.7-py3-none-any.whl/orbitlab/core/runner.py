from __future__ import annotations
import sys
import dill  # type: ignore
import traceback
import importlib.util
from pathlib import Path
from typing import Dict, Optional, Callable, Any, Union, cast
from collections.abc import MutableMapping
from io import StringIO

from orbitlab.core.validator import OrbitValidator
from orbitlab.core.cache import OrbitCache
from orbitlab.adapters.base import BaseProjectAdapter
from orbitlab.core.crypto import decrypt_hybrid, validar_firma, firmar_dill
from orbitlab.core.mutator import global_mutator
from orbitlab.core.utils import log_message

class OrbitRunner:
    def __init__(
        self,
        path: Union[str, Path],
        external_validator: Optional[Callable[[dict[str, Any]], bool]] = None,
        mutation_filter: Optional[list[str]] = None,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = False
    ) -> None:
        self.dill_path = Path(path)
        self.external_validator = external_validator
        self.mutation_filter = mutation_filter
        self.enable_cache = enable_cache
        self.cache = OrbitCache(cache_dir) if enable_cache and cache_dir else None

        self.adapter = BaseProjectAdapter()
        self.obj: MutableMapping[str, Any] = {}  
        self.payload: MutableMapping[str, Any] = {}
        self.source_code: Optional[str] = None

    def run(self, method_name: Optional[str] = None, arg: Optional[str] = None) -> Any:
        log_message(f"Validando firma para: {self.dill_path}", emoji="🔍")
        if not validar_firma(self.dill_path):
            log_message(f"Firma inválida o inexistente para: {self.dill_path}", emoji="🚫", level="error")
            return None

        if not self.load() or not self.validate():
            return None

        self.mutate()
        self._dump_and_sign()
        if not self.enable_cache:
            self._create_structure()

        if method_name:
            return self._run_method(method_name, arg)
        else:
            return self._run_function()


    def load(self) -> bool:
        cache_key = str(self.dill_path.resolve())
        cached = self.cache.get(cache_key, validate_hash=True) if self.cache else None
        if cached:
            self.obj = cached
            self.payload = self._extract_payload(self.obj)
            log_message("Usando caché con firma válida", emoji="📦")
            return True

        try:
            with self.dill_path.open("rb") as f:
                raw = dill.load(f)  # pyright: ignore[reportUnknownMemberType]

            from orbitlab.core.dynamic_store import to_plain_dict
            if isinstance(raw, dict):
                self.obj = {k: to_plain_dict(v) for k, v in raw.items()} # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
            else:
                self.obj = raw 

            self.payload = self._extract_payload(self.obj)
            return True

        except Exception as e:
            log_message(f"Error cargando .dill: {e}", level="error")
            return False


    def _extract_payload(self, obj: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if obj.get("secure") and "encrypted" in obj:
            try:
                encrypted_data = cast(dict[str, Any], obj["encrypted"])
                decrypted = decrypt_hybrid(encrypted_data)
                log_message("Payload desencriptado correctamente", emoji="🔐")
                return decrypted
            except Exception as e:
                log_message(f"Error desencriptando .dill: {e}", level="error")
                return {}
        if "payload" in obj:
            return cast(MutableMapping[str, Any], obj["payload"])
        log_message("El .dill no contiene ni 'payload' ni 'encrypted' válidos", level="error")
        return {}

    def validate(self) -> bool:
        if self.external_validator is not None:
            return True
        validator = OrbitValidator(self.dill_path, external_schema=self.external_validator)
        if not validator.run_all():
            validator.report()
            return False
        return True

    def mutate(self) -> None:
        self._load_default_mutadores()
        self.payload = global_mutator.apply(self.payload, only=self.mutation_filter)
        self.obj["payload"] = self.payload 
        if self.enable_cache and self.cache:
            self.cache.set(str(self.dill_path.resolve()), cast(Dict[str, Any], self.obj)) 

    def _dump_and_sign(self) -> None:
        try:
            with self.dill_path.open("wb") as f:
                dill.dump(self.obj, f) # type: ignore
            firmar_dill(self.dill_path)
            log_message(f"Persistido y firmado: {self.dill_path.name}", emoji="🔐")
        except Exception as e:
            log_message(f"Error al persistir/firma .dill: {e}", level="error")

    def _load_default_mutadores(self) -> None:
        posibles = list(Path.cwd().rglob("mutadores.py"))
        for archivo in posibles:
            modulo_path = archivo.resolve()
            nombre_modulo = ".".join(archivo.with_suffix("").parts)

            if nombre_modulo not in sys.modules:
                try:
                    spec = importlib.util.spec_from_file_location(nombre_modulo, str(modulo_path))
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[nombre_modulo] = mod
                        spec.loader.exec_module(mod)
                except Exception as e:
                    log_message(f"No se pudo cargar mutadores desde: {archivo} — {e}", level="warning")

    def _create_structure(self) -> None:
        for carpeta in self.payload.get("folders", []):
            try:
                Path(carpeta).mkdir(parents=True, exist_ok=True)
                log_message(f"Carpeta creada: {carpeta}", emoji="📁")
            except Exception as e:
                log_message(f"Error creando carpeta {carpeta}: {e}", level="error")

        for archivo in self.payload.get("archivos", []):
            try:
                ruta = Path(archivo["path"])
                ruta.parent.mkdir(parents=True, exist_ok=True)
                ruta.write_text(archivo.get("content", ""), encoding="utf-8")
                log_message(f"Archivo creado: {archivo['path']}", emoji="📄")
            except Exception as e:
                log_message(f"Error creando {archivo}: {e}", level="error")

    def _run_function(self) -> None:
        func = self.payload.get("function")
        if func and callable(func):
            log_message("Ejecutando función serializada desde .dill...", emoji="🧠")
            try:
                result = func()
                log_message(f"Función ejecutada con éxito {result}", emoji="✅", level="debug")
            except Exception as e:
                log_message(f"Error al ejecutar función: {e}", level="error")
            return

        source = self.payload.get("code", "")
        if not source:
            log_message("No se encontró código fuente para ejecutar", level="info")
            return

        contexto: dict[str, Any] = {"__data__": self.payload.get("data", {})}
        sys.stdout = output = StringIO()
        try:
            exec(compile(source, "<entrypoint>", "exec"), contexto)
            sys.stdout = sys.__stdout__
            captured = output.getvalue().strip()
            if captured:
                log_message(f"📤 [entrypoint stdout]:\n{captured}", emoji="✅", level="debug")
            log_message("Código ejecutado con éxito como script", emoji="✅", level="debug")
        except Exception as e:
            sys.stdout = sys.__stdout__
            traceback.print_exc()
            log_message(f"Error ejecutando entrypoint: {e}", level="error")

    def _run_method(self, method_name: str, arg: Optional[str]) -> Any:
        expose = self.payload.get("expose", {})
        class_name = expose.get("class_name")
        if not class_name:
            log_message("No se definió 'expose.class_name'", level="error")
            return None

        source = self.payload.get("code", "")
        if not source:
            log_message("No se encontró código fuente", level="error")
            return None

        contexto: dict[str, Any] = {"__data__": self.payload.get("data", {})}
        try:
            exec(source, contexto)
            cls = contexto.get(class_name)
            if not cls:
                log_message(f"Clase '{class_name}' no encontrada", level="error")
                return None

            instance = cls(contexto["__data__"])
            if not hasattr(instance, method_name):
                log_message(f"Método '{method_name}' no encontrado", level="error")
                return None

            result = getattr(instance, method_name)(arg) if arg else getattr(instance, method_name)()
            log_message(f"Método '{method_name}' ejecutado con resultado: {result}", emoji="✅", level="debug")
            return result

        except Exception as e:
            traceback.print_exc()
            log_message(f"Error ejecutando método '{method_name}': {e}", level="error")
            return None


__all__ = ["OrbitRunner"]
