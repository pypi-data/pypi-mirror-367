"""
Go backend interface for PyFunc bitwise operations.
"""

import ctypes
import os
import platform
from typing import Any, List, Union
from collections.abc import Iterable

def is_go_available() -> bool:
    """Check if Go backend is available."""
    try:
        _get_go_library()
        return True
    except (OSError, FileNotFoundError):
        return False

def _get_go_library():
    """Load the Go shared library."""
    # Determine the library file extension based on platform
    if platform.system() == "Windows":
        lib_name = "native_go.dll"
    elif platform.system() == "Darwin":
        lib_name = "libnative_go.dylib"
    else:
        lib_name = "libnative_go.so"
    
    # Look for the library in the native_go directory
    base_dir = os.path.join(os.path.dirname(__file__), "..", "native_go")
    
    # Try multiple possible locations
    possible_paths = [
        os.path.join(base_dir, lib_name),
        os.path.join(base_dir, "zig-out", "bin", lib_name),
        os.path.join(base_dir, ".zig-cache", "o", "*", lib_name),
        os.path.join(os.path.dirname(__file__), lib_name),
    ]
    
    lib_path = None
    
    # Check each path
    for path in possible_paths:
        if "*" in path:
            # Handle wildcard patterns
            import glob
            matches = glob.glob(path)
            if matches:
                lib_path = matches[0]
                break
        elif os.path.exists(path):
            lib_path = path
            break
    
    if not lib_path:
        raise FileNotFoundError(f"Go library not found: {lib_name}. Build with: go build -buildmode=c-shared")
    
    return ctypes.CDLL(lib_path)

class GoBackend:
    """Go backend for high-performance bitwise operations."""
    
    def __init__(self):
        try:
            self._lib = _get_go_library()
            self._setup_function_signatures()
            self._available = True
        except (OSError, FileNotFoundError):
            self._lib = None
            self._available = False
            raise ImportError("Go backend not available. Build with: go build -buildmode=c-shared")
    
    def _setup_function_signatures(self):
        """Setup ctypes function signatures for type safety."""
        # Bitwise operations
        self._lib.bitwise_and_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
        self._lib.bitwise_and_go.restype = None
        
        self._lib.bitwise_or_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
        self._lib.bitwise_or_go.restype = None
        
        self._lib.bitwise_xor_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
        self._lib.bitwise_xor_go.restype = None
        
        self._lib.bitwise_not_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        self._lib.bitwise_not_go.restype = None
        
        self._lib.left_shift_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
        self._lib.left_shift_go.restype = None
        
        self._lib.right_shift_go.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
        self._lib.right_shift_go.restype = None
    
    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported by Go backend."""
        if not self._available:
            return False
        
        supported_ops = {
            'bitwise_and', 'bitwise_or', 'bitwise_xor', 'bitwise_not',
            'left_shift', 'right_shift'
        }
        
        return operation in supported_ops
    
    def supports_data_type(self, data: Any) -> bool:
        """Check if data type is supported by Go backend."""
        if not self._available:
            return False
        
        # Check if it's an iterable of integers
        if not isinstance(data, Iterable) or isinstance(data, (str, bytes)):
            return False
        
        try:
            # Check if all elements can be converted to int
            data_list = list(data) if not isinstance(data, list) else data
            if not data_list:
                return True  # Empty list is supported
            
            for item in data_list[:5]:  # Check first 5 elements
                int(item)
            return True
        except (ValueError, TypeError):
            return False
    
    def _to_int_array(self, data: List[int]) -> ctypes.Array:
        """Convert Python list to ctypes int array."""
        int_data = [int(x) for x in data]
        array_type = ctypes.c_int * len(int_data)
        return array_type(*int_data)
    
    def bitwise_and(self, data: List[int], operand: int) -> List[int]:
        """Perform bitwise AND using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.bitwise_and_go(int_array, len(data), operand)
        return [int_array[i] for i in range(len(data))]
    
    def bitwise_or(self, data: List[int], operand: int) -> List[int]:
        """Perform bitwise OR using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.bitwise_or_go(int_array, len(data), operand)
        return [int_array[i] for i in range(len(data))]
    
    def bitwise_xor(self, data: List[int], operand: int) -> List[int]:
        """Perform bitwise XOR using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.bitwise_xor_go(int_array, len(data), operand)
        return [int_array[i] for i in range(len(data))]
    
    def bitwise_not(self, data: List[int]) -> List[int]:
        """Perform bitwise NOT using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.bitwise_not_go(int_array, len(data))
        return [int_array[i] for i in range(len(data))]
    
    def left_shift(self, data: List[int], bits: int) -> List[int]:
        """Perform left shift using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.left_shift_go(int_array, len(data), bits)
        return [int_array[i] for i in range(len(data))]
    
    def right_shift(self, data: List[int], bits: int) -> List[int]:
        """Perform right shift using Go backend."""
        if not data:
            return []
        
        int_array = self._to_int_array(data)
        self._lib.right_shift_go(int_array, len(data), bits)
        return [int_array[i] for i in range(len(data))]