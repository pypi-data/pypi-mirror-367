from __future__ import annotations
from typing import Callable, Dict, Any, Optional, TypeVar, MutableMapping, Generic

T = TypeVar('T', bound=MutableMapping[str, Any])

class OrbitMutator(Generic[T]):
    """
    Gestor de mutadores sobre un diccionario mutable.
    Cada mutador recibe y devuelve el mismo tipo de diccionario.
    """
    def __init__(self) -> None:
        self._mutators: Dict[str, Callable[[T], T]] = {}

    def register(self, name: str) -> Callable[[Callable[[T], T]], Callable[[T], T]]:
        """
        Decorador para registrar un mutador bajo el nombre indicado.
        """
        def wrapper(fn: Callable[[T], T]) -> Callable[[T], T]:
            if not callable(fn):
                raise ValueError(f"El mutador '{name}' no es una función válida.")
            self._mutators[name] = fn
            return fn
        return wrapper

    def apply(self, data: T, only: Optional[list[str]] = None) -> T:
        """
        Aplica los mutadores registrados al diccionario `data`.
        Si `only` es None, se aplican todos los mutators.
        Si `only` es una lista (incluso vacía), solo se aplican los mutators cuyos nombres estén en esa lista.
        """
        for name, fn in self._mutators.items():
            if only is not None and name not in only:
                continue
            data = fn(data) 
        return data


global_mutator: OrbitMutator[MutableMapping[str, Any]] = OrbitMutator()

__all__ = ["OrbitMutator", "global_mutator"]
