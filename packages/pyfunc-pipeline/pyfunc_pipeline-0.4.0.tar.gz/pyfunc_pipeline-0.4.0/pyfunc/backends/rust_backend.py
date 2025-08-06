"""
Rust backend for PyFunc statistical operations.
"""

from typing import List, Union, Any
import sys
import os

def is_rust_available() -> bool:
    """Check if Rust backend is available."""
    try:
        import native_rust
        return True
    except ImportError:
        return False

class RustBackend:
    """Rust backend for memory-safe statistical operations."""
    
    def __init__(self):
        if not is_rust_available():
            raise ImportError("Rust backend not available. Build with: python build_rust.py")
        
        import native_rust
        self._rust_module = native_rust
    
    def median(self, data: List[Union[int, float]]) -> float:
        """Calculate median using Rust backend."""
        # Convert to float list for Rust
        float_data = [float(x) for x in data]
        return self._rust_module.median(float_data)
    
    def stdev(self, data: List[Union[int, float]]) -> float:
        """Calculate standard deviation using Rust backend."""
        # Convert to float list for Rust
        float_data = [float(x) for x in data]
        return self._rust_module.stdev(float_data)
    
    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported by Rust backend."""
        supported_ops = ['median', 'stdev']
        return operation in supported_ops
    
    def supports_data_type(self, data: Any) -> bool:
        """Check if data type is supported by Rust backend."""
        try:
            # Must be iterable and contain numeric data
            if not hasattr(data, '__iter__'):
                return False
            
            # Check if we can convert to float
            for item in data:
                float(item)
            return True
        except (TypeError, ValueError):
            return False