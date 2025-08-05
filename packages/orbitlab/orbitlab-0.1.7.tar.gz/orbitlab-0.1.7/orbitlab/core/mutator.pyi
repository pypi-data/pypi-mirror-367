# orbitlab/core/mutator.pyi

from typing import Any, Callable, Generic, MutableMapping, Optional, TypeVar, List

T = TypeVar('T', bound=MutableMapping[str, Any])

class OrbitMutator(Generic[T]):
    """
    Gestor de mutadores sobre un diccionario mutable.
    """
    def __init__(self) -> None: ...
    def register(self, name: str) -> Callable[[Callable[[T], T]], Callable[[T], T]]: ...
    def apply(self, data: T, only: Optional[List[str]] = ...) -> T: ...

global_mutator: OrbitMutator[MutableMapping[str, Any]]
