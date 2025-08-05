# orbitlab/adapters/security.py

from typing import Any, Dict, List, Optional
from Crypto.PublicKey import RSA
from orbitlab.adapters.base import BaseProjectAdapter
from cross_crypto_py.encrypt import encryptHybrid
from cross_crypto_py.decrypt import decryptHybrid  
from cross_crypto_py.file_crypto import encryptFileHybrid, decryptFileHybrid  
from cross_crypto_py.keygen import generateRSAKeys  
from orbitlab.core.utils import log_message


class HybridSecurityAdapter(BaseProjectAdapter):
    """
    Adaptador de cifrado híbrido usando cross-crypto-py.
    Soporta:
      - mode="json" para datos JSON
      - mode="dill" para objetos serializados (.dill)
      - mode="binary" para bytes
    Modo streaming y cifrado de archivos/carpetas.
    Claves RSA vienen de settings.PUBLIC_KEY / PRIVATE_KEY.
    """

    def encrypt(
        self,
        data: Any,
        mode: str = "json",
        stream: bool = False,
        output_path: Optional[str] = None,
        chunk_size: int = 64 * 1024
    ) -> Dict[str, Any]:
        pub = getattr(self.settings, "PUBLIC_KEY", None)
        if not pub:
            raise ValueError("🔐 Public key not found in settings")
        log_message(f"🔐 [encrypt:{mode} stream={stream}] starting", scope="encrypt", level="debug")
        return encryptHybrid(
            data,
            pub,
            mode=mode,
            stream=stream,
            output_path=output_path,
            chunk_size=chunk_size
        )  # type: ignore

    def decrypt(
        self,
        encrypted: Dict[str, Any],
        mode: str = "json",
        stream: bool = False,
        decrypted_output_path: Optional[str] = None
    ) -> Any:
        priv = getattr(self.settings, "PRIVATE_KEY", None)
        if not priv:
            raise ValueError("🔓 Private key not found in settings")
        log_message(f"🔓 [decrypt:{mode} stream={stream}] starting", scope="decrypt", level="debug")
        return decryptHybrid(
            encrypted,
            priv,
            mode=mode,
            stream=stream,
            decrypted_output_path=decrypted_output_path
        )

    def public_key(self) -> RSA.RsaKey:
        key = getattr(self.settings, "PUBLIC_KEY", None)
        if not key:
            raise ValueError("Public key not found for import_key()")
        return RSA.import_key(key)

    def private_key(self) -> RSA.RsaKey:
        key = getattr(self.settings, "PRIVATE_KEY", None)
        if not key:
            raise ValueError("Private key not found for import_key()")
        return RSA.import_key(key)

    # Métodos de conveniencia para diferentes modos
    def encrypt_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.encrypt(data, mode="json")

    def decrypt_json(self, encrypted: Dict[str, Any]) -> Dict[str, Any]:
        return self.decrypt(encrypted, mode="json")

    def encrypt_dill(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.encrypt(data, mode="dill")

    def decrypt_dill(self, encrypted: Dict[str, Any]) -> Dict[str, Any]:
        return self.decrypt(encrypted, mode="dill")

    def encrypt_binary(self, data: bytes) -> Dict[str, Any]:
        return self.encrypt(data, mode="binary")

    def decrypt_binary(self, encrypted: Dict[str, Any]) -> bytes:
        return self.decrypt(encrypted, mode="binary")

    def encrypt_file(
        self,
        paths: List[str],
        output_enc: Optional[str] = None,
        zip_output: Optional[str] = None,
        attach_metadata: bool = True,
        save_file: bool = False
    ) -> Dict[str, Any]:
        pub = getattr(self.settings, "PUBLIC_KEY", None)
        if not pub:
            raise ValueError("Public key not found in settings")
        log_message(f"🔐 [encrypt_file] paths={paths}", scope="encrypt", level="debug")
        return encryptFileHybrid(
            paths=paths,
            public_key=pub,
            output_enc=output_enc,
            zip_output=zip_output,
            attach_metadata=attach_metadata,
            save_file=save_file
        )

    def decrypt_file(
        self,
        enc_path: str,
        extract_to: Optional[str] = None,
        cleanup_zip: bool = True
    ) -> str:
        priv = getattr(self.settings, "PRIVATE_KEY", None)
        if not priv:
            raise ValueError("Private key not found in settings")
        log_message(f"🔓 [decrypt_file] enc_path={enc_path}", scope="decrypt", level="debug")
        return decryptFileHybrid(
            enc_path=enc_path,
            private_key=priv,
            extract_to=extract_to,
            cleanup_zip=cleanup_zip
        )

    def generate_keys(
        self,
        bits: int = 4096,
        password: Optional[bytes] = None,
        verbose: bool = False
    ) -> Dict[str, str]:
        """Wrapper para crear un par de claves RSA."""
        return generateRSAKeys(bits=bits, password=password, verbose=verbose)
