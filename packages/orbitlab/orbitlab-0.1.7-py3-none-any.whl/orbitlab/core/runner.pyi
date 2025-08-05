# orbitlab/core/runner.pyi

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

__all__ = ["OrbitRunner"]

class OrbitRunner:
    dill_path: Path
    external_validator: Optional[Callable[[Dict[str, Any]], bool]]
    mutation_filter: Optional[List[str]]
    enable_cache: bool
    cache: Optional[Any]
    adapter: Any
    obj: MutableMapping[str, Any]
    payload: MutableMapping[str, Any]
    source_code: Optional[str]

    def __init__(
        self,
        path: Union[str, Path],
        external_validator: Optional[Callable[[Dict[str, Any]], bool]] = ...,
        mutation_filter: Optional[List[str]] = ...,
        cache_dir: Optional[Path] = ...,
        enable_cache: bool = ...
    ) -> None: ...
    def run(
        self,
        method_name: Optional[str] = ...,
        arg: Optional[str] = ...
    ) -> Any: ...
    def load(self) -> bool: ...
    def validate(self) -> bool: ...
    def mutate(self) -> None: ...
