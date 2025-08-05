# orbitlab/adapters/security.pyi

from typing import Any, Dict, List, Optional
from Crypto.PublicKey.RSA import RsaKey
from orbitlab.adapters.base import BaseProjectAdapter


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
        mode: str = ...,
        stream: bool = ...,
        output_path: Optional[str] = ...,
        chunk_size: int = ...
    ) -> Dict[str, Any]: ...

    def decrypt(
        self,
        encrypted: Dict[str, Any],
        mode: str = ...,
        stream: bool = ...,
        decrypted_output_path: Optional[str] = ...
    ) -> Any: ...

    def public_key(self) -> RsaKey: ...

    def private_key(self) -> RsaKey: ...

    def encrypt_json(self, data: Dict[str, Any]) -> Dict[str, Any]: ...

    def decrypt_json(self, encrypted: Dict[str, Any]) -> Dict[str, Any]: ...

    def encrypt_dill(self, data: Dict[str, Any]) -> Dict[str, Any]: ...

    def decrypt_dill(self, encrypted: Dict[str, Any]) -> Dict[str, Any]: ...

    def encrypt_binary(self, data: bytes) -> Dict[str, Any]: ...

    def decrypt_binary(self, encrypted: Dict[str, Any]) -> bytes: ...

    def encrypt_file(
        self,
        paths: List[str],
        output_enc: Optional[str] = ...,
        zip_output: Optional[str] = ...,
        attach_metadata: bool = ...,
        save_file: bool = ...
    ) -> Dict[str, Any]: ...

    def decrypt_file(
        self,
        enc_path: str,
        extract_to: Optional[str] = ...,
        cleanup_zip: bool = ...
    ) -> str: ...

    def generate_keys(
        self,
        bits: int = ...,
        password: Optional[bytes] = ...,
        verbose: bool = ...
    ) -> Dict[str, str]: ...
