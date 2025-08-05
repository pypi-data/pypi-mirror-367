# OrbitLab 🛰️

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/) [![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE) [![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen.svg)]() [![Made with ♥](https://img.shields.io/badge/made%20with-%E2%99%A5-red.svg)]()

**Orbit Lab** es un motor avanzado para la ejecución segura de estructuras **.dill** en **Python**. Integra validación estructural, ejecución dinámica de funciones y clases, transformación del payload mediante mutaciones encadenadas, cacheo inteligente, cifrado híbrido (RSA + AES), firma digital, y un sistema de almacenamiento con versionado y rollback automático.

---

## 🚀 Características principales

- ✅ **Runner dinámico** para ejecutar funciones, clases o scripts desde `.dill`.
- 🔧 **Sistema de mutadores** encadenables para transformar payloads fácilmente.
- 🧠 **Validador estructural** extensible para asegurar integridad del payload.
- 🛡️ **Cifrado híbrido (RSA + AES)** con firmas digitales para máxima seguridad.
- 🧬 **Almacenamiento versiónado** vía `DynamicDillStore` con rollback.
- ♻️ **Cacheo inteligente** basado en hash para acelerar cargas repetidas.

---

## 📦 Estructura del Proyecto

```md
📦orbit/
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── README.md
├── orbitlab/
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── security.py
│   └── core/
│       ├── __init__.py
│       ├── cache.py
│       ├── config.py
│       ├── crypto.py
│       ├── dynamic_store.py
│       ├── logger.py
│       ├── mutator.py
│       ├── registry.py
│       ├── runner.py
│       ├── utils.py
│       └── validator.py
└── pyproject.toml
```

---

## 🧩 Componentes

| Módulo                  | Descripción |
|--------------------------|-------------|
| `orbitlab.core.runner`      | Ejecuta `.dill` como scripts, funciones o clases. |
| `orbitlab.core.mutator`     | Registra y aplica transformaciones al payload. |
| `orbitlab.core.validator`   | Valida estructura del `.dill` antes de ejecutar. |
| `orbitlab.core.crypto`      | Firma digital y cifrado híbrido. |
| `orbitlab.core.dynamic_store` | Almacenamiento tipo base de datos con rollback/versionado. |
| `orbitlab.core.cache`       | Mecanismo de cacheo basado en hash. |
| `orbitlab.core.registry`       | Registro de versiones .dill con metadatos como autor, hash, timestamp y etiquetas. |
| `orbitlab.core.validator`       | Valida firmas, claves mínimas del payload, y soporta validadores externos. |

---

## 🔐 Seguridad

- ✍️ Firmas digitales (`.dill.sig`)
- 📦 Validación automática de integridad
- 🔐 Desencriptado híbrido usando `cross-crypto-py`
- 🚫 Bloqueo de ejecución si el archivo fue alterado

---

## 🧩 Ejemplos de uso con `OrbitRunner`

### `Ejemplo 1: Uso de OrbitRunner y firma`

```python
import dill
import os
from pathlib import Path
from orbitlab.core.crypto import firmar_dill
from orbitlab.core.runner import OrbitRunner

print("🚀 Test 1: Ejecución de función serializada con OrbitRunner")

# Directorio específico para este test
base = Path("test1")
base.mkdir(exist_ok=True)
ruta = base / "mi_modelo.dill"

def hola_mundo():
    return "👋 Hola desde OrbitRunner"

payload = {
    "payload": {
        "function": hola_mundo,
        "folders": [],  
        "archivos": [],
        "code": "",
    }
}

with ruta.open("wb") as f:
    dill.dump(payload, f)

firmar_dill(ruta)

runner = OrbitRunner(str(ruta))
runner.run()

print("✅ Test 1 finalizado con ejecución directa exitosa")
print("Archivos en", base, ":", os.listdir(base))
```

### `Ejemplo 2: Una clase y mutaciones`

```python
import dill
import os
from pathlib import Path
from orbitlab.core.crypto import firmar_dill
from orbitlab.core.runner import OrbitRunner
from orbitlab.core import global_mutator

print("🔧 Test 2: Clase + método + mutaciones encadenadas + creación de carpetas")

# Directorio específico para este test
base = Path("test2")
base.mkdir(exist_ok=True)
ruta = base / "mi_modelo_mutado.dill"
carpeta_obj = base / "saludos"
archivo_obj = base / "bienvenida.txt"

@global_mutator.register("inject_data")
def inject_data(payload):
    print("🔧 inject_data aplicado")
    payload.setdefault("data", {})["quien"] = "mutado"
    return payload

@global_mutator.register("normalize_data")
def normalize_data(payload):
    print("🔧 normalize_data aplicado")
    if "quien" in payload.get("data", {}):
        payload["data"]["quien"] = payload["data"]["quien"].capitalize()
    return payload

codigo = """
class Saludo:
    def __init__(self, data):
        self.quien = data.get("quien", "nadie")

    def saludo(self):
        return f"🌟 Hola desde mutación, {self.quien}!"
"""

payload = {
    "payload": {
        "code": codigo,
        "data": {},
        "expose": {
            "class_name": "Saludo",
            "methods": [{"name": "saludo"}]
        },
        # Ahora pedimos crear carpeta y archivo en base/
        "folders": [str(carpeta_obj)],
        "archivos": [
            {"path": str(archivo_obj), "content": "¡Hola!"}
        ],
    }
}

with ruta.open("wb") as f:
    dill.dump(payload, f)

firmar_dill(ruta)

runner = OrbitRunner(
    str(ruta),
    mutation_filter=["inject_data", "normalize_data"]
)
runner.run("saludo")

print("✅ Test 2 finalizado con mutaciones y creación de:", os.listdir(base))
print("· Carpeta 'saludos' existe?", carpeta_obj.is_dir())
print("· Archivo 'bienvenida.txt' existe?", archivo_obj.is_file())
```

---

### `Ejemplo 3: Uso con DynamicDillStore` 🧠

```python
import os
from pathlib import Path
from orbitlab.core.dynamic_store import DynamicDillStore

print("📦 Test 3: DynamicDillStore commit y rollback")

# Definimos un directorio y fichero de entrada
base_dir = Path("test3_commit_rollback/entrada")
base_dir.mkdir(parents=True, exist_ok=True)
path = base_dir / "data.dill"

# Crear store (auto_save creará data.dill)
store = DynamicDillStore(str(path), auto_save=True)
print("Store inicializado, existe?", path.exists())

# Setear y commitear valores iniciales
store.set("params", {"a": 1, "b": 2})
print("📝 Valores iniciales guardados:", store.get("params"))

store.commit("params")
versions_dir = Path(str(path) + ".versions")
print("🔐 Commit realizado, versiones:", os.listdir(versions_dir))

# Hacemos un cambio y otro commit
store.set("params", {"a": 2, "b": 3})
store.commit("params")
print("🔐 Segundo commit, versiones:", os.listdir(versions_dir))

# Listar history y rollback a la primera versión
history = store.history("params")
print("🕒 History timestamps:", history)
first_ts = history[0]

store.rollback("params", first_ts)
print("↩️ Rollback a", first_ts, "->", store.get("params"))

```

---

## 📁 Formato esperado del `.dill`

```python
{
  "payload": {
    "code": "...",  
    "function": ..., 
    "data": {...},  
    "expose": {
      "class_name": "MyClass",
      "methods": [{"name": "do"}]
    },
    "folders": [],
    "archivos": []
  }
}
```

---

## ⚙️ Requisitos

- Python 3.10+
- `dill`, `filelock`, `cross-crypto-py`, `pydantic-settings`

---

## 🪪 Licencia

BSD 3-Clause License © 2025 Jose Fabian Soltero Escobar
