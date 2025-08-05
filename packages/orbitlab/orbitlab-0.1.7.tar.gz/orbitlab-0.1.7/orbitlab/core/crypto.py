# orbitlab/core/crypto.py

import json
import hashlib
import bcrypt
from pathlib import Path
from typing import Any, Dict, Optional
from Crypto.PublicKey import RSA
from orbitlab.adapters.security import HybridSecurityAdapter

_adapter = HybridSecurityAdapter()


def firmar_dill(dill_path: Path, hash_algoritmo: str = "blake2b") -> Path:
    """
    Genera una firma .sig basada en el hash del archivo .dill.
    """
    hash_func = getattr(hashlib, hash_algoritmo, hashlib.blake2b)
    contenido = dill_path.read_bytes()
    hash_val = hash_func(contenido).hexdigest()
    firma = {
        "file": dill_path.name,
        "hash": f"{hash_algoritmo}:{hash_val}"
    }
    sig_path = dill_path.with_suffix(".dill.sig")
    sig_path.write_text(json.dumps(firma, indent=2), encoding="utf-8")
    return sig_path


def validar_firma(dill_path: Path) -> bool:
    """
    Verifica la integridad de un archivo .dill usando su .sig asociado.
    """
    sig_path = dill_path.with_suffix(".dill.sig")
    if not sig_path.exists():
        return False

    try:
        firma = json.loads(sig_path.read_text(encoding="utf-8"))
        algoritmo, valor_firma = firma["hash"].split(":", 1)
        hash_func = getattr(hashlib, algoritmo, hashlib.blake2b)
        contenido = dill_path.read_bytes()
        return hash_func(contenido).hexdigest() == valor_firma
    except Exception:
        return False


def encrypt_hybrid(data: Any, **opts: Any) -> Dict[str, Any]:
    """
    Encripta datos usando el adaptador híbrido.
    Opciones admitidas en opts: mode, stream, output_path, chunk_size.
    """
    return _adapter.encrypt(data, **opts)


def decrypt_hybrid(encrypted: Dict[str, Any], **opts: Any) -> Any:
    """
    Desencripta datos usando el adaptador híbrido.
    Opciones admitidas en opts: mode, stream, decrypted_output_path.
    """
    return _adapter.decrypt(encrypted, **opts)


def load_public_key() -> RSA.RsaKey:
    """
    Devuelve la clave pública RSA cargada vía el adaptador.
    """
    return _adapter.public_key()


def load_private_key() -> RSA.RsaKey:
    """
    Devuelve la clave privada RSA cargada vía el adaptador.
    """
    return _adapter.private_key()


def hash_text(password: str, encoding: str = "utf-8") -> str:
    """
    Hashea un texto usando bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(encoding), salt).decode(encoding)


def verify_hash_text(text: str, hashed: str, encoding: str = "utf-8") -> bool:
    """
    Verifica un texto contra un hash bcrypt.
    """
    return bcrypt.checkpw(text.encode(encoding), hashed.encode(encoding))


def generate_rsa_keys(
    bits: int = 4096,
    password: Optional[bytes] = None,
    verbose: bool = False
) -> Dict[str, str]:
    """
    Genera un par de claves RSA delegando al adaptador.
    """
    return _adapter.generate_keys(bits=bits, password=password, verbose=verbose)
