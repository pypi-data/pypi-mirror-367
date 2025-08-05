
"""
Quantum File System (QFS)

A secure web-based file conversion system that encrypts JSON files into QJSON format 
using custom quantum-inspired encryption algorithms.
"""

__version__ = "0.1.0"
__author__ = "QFS Development Team"
__email__ = "dev@qfs.example.com"
__license__ = "MIT"

from .quantum_cipher import QuantumJSONConverter, QuantumFileSystemCustom
from .converter import QuantumConverter
from .file_system import QuantumFileSystem

__all__ = [
    "QuantumJSONConverter",
    "QuantumFileSystemCustom", 
    "QuantumConverter",
    "QuantumFileSystem",
]
