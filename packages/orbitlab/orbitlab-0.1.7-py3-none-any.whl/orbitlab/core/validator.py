import dill  # type: ignore
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List, Union

from orbitlab.core.crypto import decrypt_hybrid, validar_firma
from orbitlab.core.utils import log_message


class OrbitValidator:
    """
    Valida un archivo .dill asegurando:
    - Firma válida.
    - Correcta deserialización.
    - Presencia de claves estándar de Orbit: folders, archivos, code.
    - Validación externa opcional.
    """

    def __init__(
        self,
        dill_path: Union[str, Path],
        external_schema: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        self.dill_path = Path(dill_path)
        self.external_schema = external_schema
        self.errors: List[str] = []
        self.payload: Dict[str, Any] = {}

    def validate_firma(self) -> bool:
        if not validar_firma(self.dill_path):
            msg = f"❌ Firma inválida o no encontrada para {self.dill_path}"
            self.errors.append(msg)
            log_message(msg, level="error")
            return False

        log_message("🔏 Firma válida confirmada", level="info")
        return True

    def validate_estructura(self) -> bool:
        try:
            with self.dill_path.open("rb") as f:
                data = dill.load(f)  # type: ignore
        except Exception as e:
            msg = f"❌ Error al deserializar .dill: {e}"
            self.errors.append(msg)
            log_message(msg, level="error")
            return False

        if not isinstance(data, dict):
            msg = "❌ El contenido no es un diccionario."
            self.errors.append(msg)
            log_message(msg, level="error")
            return False

        if data.get("secure") and "encrypted" in data:  # type: ignore
            log_message("🔐 Contenido cifrado detectado. Intentando desencriptar...", level="debug")
            try:
                self.payload = decrypt_hybrid(data["encrypted"])  # type: ignore
                log_message("✅ Contenido desencriptado exitosamente", level="debug")
            except Exception as e:
                msg = f"❌ Error desencriptando: {e}"
                self.errors.append(msg)
                log_message(msg, level="error")
                return False

        elif "payload" in data:
            self.payload = data["payload"]  # type: ignore
        else:
            msg = "❌ No se encontró clave 'payload' o 'encrypted'."
            self.errors.append(msg)
            log_message(msg, level="error")
            return False

        # Validar las claves obligatorias
        for key in ("folders", "archivos", "code"):
            if key not in self.payload:  # type: ignore
                msg = f"❌ Falta la clave obligatoria: {key}"
                self.errors.append(msg)
                log_message(msg, level="error")

        return not self.errors

    def validate_externo(self) -> bool:
        if self.external_schema:
            log_message("🧪 Ejecutando validador externo...", level="debug")
            try:
                valid = self.external_schema(self.payload)  # type: ignore
            except Exception as e:
                msg = f"❌ Excepción en validador externo: {e}"
                self.errors.append(msg)
                log_message(msg, level="error")
                return False

            if not valid:
                msg = "❌ Validador externo retornó False."
                self.errors.append(msg)
                log_message(msg, level="error")
                return False

        return True

    def run_all(self) -> bool:
        log_message(f"📍 Validando archivo: {self.dill_path}", level="debug")

        if not self.dill_path.exists():
            msg = f"❌ Archivo no encontrado: {self.dill_path}"
            self.errors.append(msg)
            log_message(msg, level="error")
            return False

        return (
            self.validate_firma() 
            and self.validate_estructura() 
            and self.validate_externo()
        )

    def report(self) -> None:
        if self.errors:
            for err in self.errors:
                log_message(err, level="error")
        else:
            log_message("✅ Validación completada sin errores", level="info")
