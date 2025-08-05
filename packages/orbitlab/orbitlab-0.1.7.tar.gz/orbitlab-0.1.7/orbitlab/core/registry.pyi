# orbitlab/core/registry.pyi

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["OrbitRegistry"]

class OrbitRegistry:
    registry_path: Path
    data: Dict[str, Dict[str, Any]]

    def __init__(self, registry_path: Path) -> None: ...
    def register(
        self,
        dill_file: Path,
        author: str = ...,
        tags: Optional[List[str]] = ...,
        description: str = ...
    ) -> Tuple[str, Dict[str, Any]]: ...
    def list_versions(
        self,
        file_name: str
    ) -> Dict[str, Dict[str, Any]]: ...
    def get_entry(
        self,
        version_key: str
    ) -> Optional[Dict[str, Any]]: ...
    def remove_entry(
        self,
        version_key: str
    ) -> bool: ...
