"""
Backend selection logic for PyFunc operations.
"""

from typing import Any, Callable, Optional, Union, List
from ..placeholder import Placeholder

class BackendSelector:
    """Selects the appropriate backend for pipeline operations."""
    
    def __init__(self):
        self.cpp_enabled = False
        self.cpp_threshold = 10000
        self.rust_threshold = 1000  # Lower threshold for Rust due to overhead
        self.zig_threshold = 5000   # Medium threshold for Zig (fast but has FFI overhead)
        self.go_threshold = 1000    # Threshold for Go bitwise operations
        self._python_backend = None
        self._cpp_backend = None
        self._zig_backend = None
        self._go_backend = None
        self._rust_backend = None
    
    def enable_cpp(self, threshold: int = 10000):
        """Enable C++ backend with size threshold."""
        try:
            from .cpp_backend import CppBackend, is_cpp_available
            if is_cpp_available():
                self.cpp_enabled = True
                self.cpp_threshold = threshold
                if self._cpp_backend is None:
                    self._cpp_backend = CppBackend()
                print(f"C++ backend enabled (threshold: {threshold})")
            else:
                print("❌ C++ backend not available, falling back to Python")
                self.cpp_enabled = False
        except ImportError:
            print("❌ C++ backend not compiled, falling back to Python")
            self.cpp_enabled = False
    
    def force_cpp(self):
        """Force use of C++ backend for all supported operations (no threshold)."""
        try:
            from .cpp_backend import CppBackend, is_cpp_available
            if is_cpp_available():
                self.cpp_enabled = True
                self.cpp_threshold = 0  # No threshold - use for all operations
                if self._cpp_backend is None:
                    self._cpp_backend = CppBackend()
                print("🚀 C++ backend forced for all supported operations")
            else:
                print("❌ C++ backend not available, falling back to Python")
                self.cpp_enabled = False
        except ImportError:
            print("❌ C++ backend not compiled, falling back to Python")
            self.cpp_enabled = False
    
    def disable_cpp(self):
        """Disable C++ backend."""
        self.cpp_enabled = False
        print("🐍 Using Python backend only")
    
    def set_rust_threshold(self, threshold: int = 1000):
        """Set the threshold for Rust backend usage."""
        self.rust_threshold = threshold
        print(f"🦀 Rust backend threshold set to {threshold}")
    
    @property
    def rust_backend(self):
        """Get Rust backend instance."""
        if self._rust_backend is None:
            try:
                from .rust_backend import RustBackend, is_rust_available
                if is_rust_available():
                    self._rust_backend = RustBackend()
            except ImportError:
                pass
        return self._rust_backend
    
    def should_use_rust(self, data: Any, operation: str) -> bool:
        """Determine if Rust backend should be used for statistical operations."""
        if self._rust_backend is None:
            return False
        
        if operation not in ['median', 'stdev']:
            return False
        
        try:
            data_size = len(data) if hasattr(data, '__len__') else 0
            return data_size >= self.rust_threshold
        except:
            return False
    
    def set_zig_threshold(self, threshold: int = 5000):
        """Set the threshold for Zig backend usage."""
        self.zig_threshold = threshold
        print(f"⚡ Zig backend threshold set to {threshold}")
    
    @property
    def zig_backend(self):
        """Get Zig backend instance."""
        if self._zig_backend is None:
            try:
                from .zig_backend import ZigBackend, is_zig_available
                if is_zig_available():
                    self._zig_backend = ZigBackend()
            except ImportError:
                pass
        return self._zig_backend
    
    def should_use_zig(self, data: Any, operation: str) -> bool:
        """Determine if Zig backend should be used for mathematical operations."""
        if self._zig_backend is None:
            return False
        
        # Zig specializes in mathematical operations
        zig_operations = ['sum', 'mean', 'min', 'max', 'stdev', 'map_multiply', 'map_add', 'map_power']
        if operation not in zig_operations:
            return False
        
        try:
            data_size = len(data) if hasattr(data, '__len__') else 0
            return data_size >= self.zig_threshold
        except:
            return False
    
    def set_go_threshold(self, threshold: int = 1000):
        """Set the threshold for Go backend usage."""
        self.go_threshold = threshold
        print(f"🔧 Go backend threshold set to {threshold}")
    
    @property
    def go_backend(self):
        """Get Go backend instance."""
        if self._go_backend is None:
            try:
                from .go_backend import GoBackend, is_go_available
                if is_go_available():
                    self._go_backend = GoBackend()
            except ImportError:
                pass
        return self._go_backend
    
    def should_use_go(self, data: Any, operation: str) -> bool:
        """Determine if Go backend should be used for bitwise operations."""
        if self._go_backend is None:
            return False
        
        # Go specializes in bitwise operations
        go_operations = ['bitwise_and', 'bitwise_or', 'bitwise_xor', 'bitwise_not', 'left_shift', 'right_shift']
        if operation not in go_operations:
            return False
        
        try:
            data_size = len(data) if hasattr(data, '__len__') else 0
            return data_size >= self.go_threshold
        except:
            return False
    
    @property
    def python_backend(self):
        """Get Python backend instance."""
        if self._python_backend is None:
            from .python_backend import PythonBackend
            self._python_backend = PythonBackend()
        return self._python_backend
    
    @property
    def cpp_backend(self):
        """Get C++ backend instance."""
        if self._cpp_backend is None:
            try:
                from .cpp_backend import CppBackend, is_cpp_available
                if is_cpp_available():
                    self._cpp_backend = CppBackend()
            except ImportError:
                pass
        return self._cpp_backend
    
    def should_use_cpp(self, data: Any, operation: str, func: Any = None) -> bool:
        """Determine if C++ backend should be used."""
        if not self.cpp_enabled or self._cpp_backend is None:
            return False
        
        # Check data size
        try:
            data_size = len(data) if hasattr(data, '__len__') else 0
            if data_size < self.cpp_threshold:
                return False
        except:
            return False
        
        # Check if operation is supported
        if not self._cpp_backend.supports_operation(operation, func):
            return False
        
        # Check data type compatibility
        if not self._cpp_backend.supports_data_type(data):
            return False
        
        return True
    
    def execute_map(self, data: Any, func: Callable) -> Any:
        """Execute map operation with appropriate backend."""
        if self.should_use_cpp(data, 'map', func):
            return self._cpp_backend.map(data, func)
        return self.python_backend.map(data, func)
    
    def execute_filter(self, data: Any, predicate: Callable) -> Any:
        """Execute filter operation with appropriate backend."""
        if self.should_use_cpp(data, 'filter', predicate):
            return self._cpp_backend.filter(data, predicate)
        return self.python_backend.filter(data, predicate)
    
    def execute_reduce(self, data: Any, func: Callable, initializer: Any = None) -> Any:
        """Execute reduce operation with appropriate backend."""
        if self.should_use_cpp(data, 'reduce', func):
            return self._cpp_backend.reduce(data, func, initializer)
        return self.python_backend.reduce(data, func, initializer)
    
    def execute_sum(self, data: Any) -> Union[int, float]:
        """Execute sum operation with appropriate backend."""
        if self.should_use_cpp(data, 'sum'):
            return self._cpp_backend.sum(data)
        return self.python_backend.sum(data)