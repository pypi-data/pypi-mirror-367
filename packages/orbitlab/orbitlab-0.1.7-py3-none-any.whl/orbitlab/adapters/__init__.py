# orbitlab/adapters/__init__.py

"""
Adaptadores externos para Orbit Lab.
Incluye soporte para configuración heredada y cifrado híbrido con claves externas.
"""

from orbitlab.adapters.base import BaseProjectAdapter
from orbitlab.adapters.security import HybridSecurityAdapter

__all__ = [
    "BaseProjectAdapter",
    "HybridSecurityAdapter"
]
