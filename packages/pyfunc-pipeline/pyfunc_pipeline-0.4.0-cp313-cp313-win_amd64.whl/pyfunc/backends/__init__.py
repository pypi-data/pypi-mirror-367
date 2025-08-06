"""
PyFunc C++ Backend System

This module provides C++ acceleration for computation-heavy operations
while maintaining full compatibility with the Python API.
"""

from .python_backend import PythonBackend
from .cpp_backend import CppBackend, is_cpp_available
from .backend_selector import BackendSelector

# Global backend selector
_backend_selector = BackendSelector()

def enable_cpp_backend(threshold: int = 10000):
    """Enable C++ backend for operations above the threshold size."""
    _backend_selector.enable_cpp(threshold)

def disable_cpp_backend():
    """Disable C++ backend, use Python only."""
    _backend_selector.disable_cpp()

def use_cpp_backend():
    """Force use of C++ backend for all supported operations (no threshold)."""
    _backend_selector.force_cpp()

def set_rust_threshold(threshold: int = 1000):
    """Set the threshold for Rust backend usage (default: 1000)."""
    _backend_selector.set_rust_threshold(threshold)

def set_zig_threshold(threshold: int = 5000):
    """Set the threshold for Zig backend usage (default: 5000)."""
    _backend_selector.set_zig_threshold(threshold)

def is_zig_available():
    """Check if Zig backend is available."""
    try:
        from .zig_backend import is_zig_available
        return is_zig_available()
    except ImportError:
        return False

def set_go_threshold(threshold: int = 1000):
    """Set the threshold for Go backend usage (default: 1000)."""
    _backend_selector.set_go_threshold(threshold)

def is_go_available():
    """Check if Go backend is available."""
    try:
        from .go_backend import is_go_available
        return is_go_available()
    except ImportError:
        return False

def get_backend():
    """Get the current backend selector."""
    return _backend_selector

__all__ = [
    'PythonBackend',
    'CppBackend', 
    'is_cpp_available',
    'is_zig_available',
    'is_go_available',
    'BackendSelector',
    'enable_cpp_backend',
    'disable_cpp_backend',
    'use_cpp_backend',
    'set_rust_threshold',
    'set_zig_threshold',
    'set_go_threshold',
    'get_backend'
]