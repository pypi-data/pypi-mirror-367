"""
Zig backend interface for PyFunc mathematical operations.
"""

import ctypes
import os
import platform
from typing import Any, List, Union
from collections.abc import Iterable

def is_zig_available() -> bool:
    """Check if Zig backend is available."""
    try:
        _get_zig_library()
        return True
    except (OSError, FileNotFoundError):
        return False

def _get_zig_library():
    """Load the Zig shared library."""
    # Determine the library file extension based on platform
    if platform.system() == "Windows":
        lib_name = "pyfunc_zig.dll"
    elif platform.system() == "Darwin":
        lib_name = "libpyfunc_zig.dylib"
    else:
        lib_name = "libpyfunc_zig.so"
    
    # Look for the library in the native_zig directory
    base_dir = os.path.join(os.path.dirname(__file__), "..", "native_zig")
    
    # Try multiple possible locations
    alt_paths = [
        os.path.join(base_dir, lib_name),
        os.path.join(base_dir, "zig-out", "lib", lib_name),
        os.path.join(base_dir, "zig-out", "bin", lib_name),
        os.path.join(base_dir, ".zig-cache", "o", "*", lib_name),  # Wildcard pattern
        os.path.join(os.path.dirname(__file__), lib_name),
    ]
    
    lib_path = None
    
    # Check each path
    for path in alt_paths:
        if "*" in path:
            # Handle wildcard patterns
            import glob
            matches = glob.glob(path)
            if matches:
                lib_path = matches[0]  # Use first match
                break
        elif os.path.exists(path):
            lib_path = path
            break
    
    if not lib_path:
        raise FileNotFoundError(f"Zig library not found: {lib_name}. Tried: {alt_paths}")
    
    return ctypes.CDLL(lib_path)

class ZigBackend:
    """Zig backend for high-performance mathematical operations."""
    
    def __init__(self):
        try:
            self._lib = _get_zig_library()
            self._setup_function_signatures()
            self._available = True
        except (OSError, FileNotFoundError):
            self._lib = None
            self._available = False
            raise ImportError("Zig backend not available. Build with: zig build")
    
    def _setup_function_signatures(self):
        """Setup ctypes function signatures for type safety."""
        # Sum operations
        self._lib.zig_sum_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_sum_f64.restype = ctypes.c_double
        
        self._lib.zig_sum_i32.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_size_t]
        self._lib.zig_sum_i32.restype = ctypes.c_int64
        
        # Statistical operations
        self._lib.zig_mean_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_mean_f64.restype = ctypes.c_double
        
        self._lib.zig_min_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_min_f64.restype = ctypes.c_double
        
        self._lib.zig_max_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_max_f64.restype = ctypes.c_double
        
        self._lib.zig_std_dev_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_std_dev_f64.restype = ctypes.c_double
        
        # Map operations
        self._lib.zig_map_multiply_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_double]
        self._lib.zig_map_multiply_f64.restype = None
        
        self._lib.zig_map_add_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_double]
        self._lib.zig_map_add_f64.restype = None
        
        self._lib.zig_map_power_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_double]
        self._lib.zig_map_power_f64.restype = None
        
        # Vector operations
        self._lib.zig_dot_product_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_dot_product_f64.restype = ctypes.c_double
        
        self._lib.zig_vector_magnitude_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self._lib.zig_vector_magnitude_f64.restype = ctypes.c_double
        
        # Batch operations
        self._lib.zig_batch_stats_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
        self._lib.zig_batch_stats_f64.restype = None
        
        self._lib.zig_batch_basic_f64.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
        self._lib.zig_batch_basic_f64.restype = None
    
    def supports_operation(self, operation: str, data_type: type = None) -> bool:
        """Check if operation is supported by Zig backend."""
        if not self._available:
            return False
        
        supported_ops = {
            'sum', 'mean', 'min', 'max', 'std_dev', 'variance',
            'map_multiply', 'map_add', 'map_power',
            'dot_product', 'vector_magnitude', 'cumsum', 'diff'
        }
        
        return operation in supported_ops
    
    def supports_data_type(self, data: Any) -> bool:
        """Check if data type is supported by Zig backend."""
        if not self._available:
            return False
        
        # Check if it's a numeric iterable
        if not isinstance(data, Iterable) or isinstance(data, (str, bytes)):
            return False
        
        # Check if all elements are numeric
        try:
            # Convert to list and check first few elements
            data_list = list(data) if not isinstance(data, list) else data
            if not data_list:
                return True  # Empty list is supported
            
            # Check if elements can be converted to float
            for item in data_list[:5]:  # Check first 5 elements
                float(item)
            return True
        except (ValueError, TypeError):
            return False
    
    def _to_float_array(self, data: List[Union[int, float]]) -> ctypes.Array:
        """Convert Python list to ctypes float array."""
        float_data = [float(x) for x in data]
        array_type = ctypes.c_double * len(float_data)
        return array_type(*float_data)
    
    def _to_int_array(self, data: List[int]) -> ctypes.Array:
        """Convert Python list to ctypes int array."""
        array_type = ctypes.c_int32 * len(data)
        return array_type(*data)
    
    def sum(self, data: List[Union[int, float]]) -> Union[int, float]:
        """Calculate sum using Zig backend."""
        if not data:
            return 0
        
        # Try integer sum first if all elements are integers
        if all(isinstance(x, int) for x in data):
            int_array = self._to_int_array(data)
            return self._lib.zig_sum_i32(int_array, len(data))
        else:
            float_array = self._to_float_array(data)
            return self._lib.zig_sum_f64(float_array, len(data))
    
    def mean(self, data: List[Union[int, float]]) -> float:
        """Calculate mean using Zig backend."""
        if not data:
            return 0.0
        
        float_array = self._to_float_array(data)
        return self._lib.zig_mean_f64(float_array, len(data))
    
    def min(self, data: List[Union[int, float]]) -> Union[int, float]:
        """Calculate minimum using Zig backend."""
        if not data:
            raise ValueError("min() arg is an empty sequence")
        
        float_array = self._to_float_array(data)
        return self._lib.zig_min_f64(float_array, len(data))
    
    def max(self, data: List[Union[int, float]]) -> Union[int, float]:
        """Calculate maximum using Zig backend."""
        if not data:
            raise ValueError("max() arg is an empty sequence")
        
        float_array = self._to_float_array(data)
        return self._lib.zig_max_f64(float_array, len(data))
    
    def stdev(self, data: List[Union[int, float]]) -> float:
        """Calculate standard deviation using Zig backend."""
        if len(data) < 2:
            raise ValueError("stdev() requires at least two data points")
        
        float_array = self._to_float_array(data)
        return self._lib.zig_std_dev_f64(float_array, len(data))
    
    def map_multiply(self, data: List[Union[int, float]], multiplier: float) -> List[float]:
        """Multiply all elements by a constant using Zig backend."""
        if not data:
            return []
        
        float_array = self._to_float_array(data)
        self._lib.zig_map_multiply_f64(float_array, len(data), multiplier)
        return [float_array[i] for i in range(len(data))]
    
    def map_add(self, data: List[Union[int, float]], addend: float) -> List[float]:
        """Add a constant to all elements using Zig backend."""
        if not data:
            return []
        
        float_array = self._to_float_array(data)
        self._lib.zig_map_add_f64(float_array, len(data), addend)
        return [float_array[i] for i in range(len(data))]
    
    def map_power(self, data: List[Union[int, float]], exponent: float) -> List[float]:
        """Raise all elements to a power using Zig backend."""
        if not data:
            return []
        
        float_array = self._to_float_array(data)
        self._lib.zig_map_power_f64(float_array, len(data), exponent)
        return [float_array[i] for i in range(len(data))]
    
    def dot_product(self, a: List[Union[int, float]], b: List[Union[int, float]]) -> float:
        """Calculate dot product of two vectors using Zig backend."""
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")
        
        if not a:
            return 0.0
        
        array_a = self._to_float_array(a)
        array_b = self._to_float_array(b)
        return self._lib.zig_dot_product_f64(array_a, array_b, len(a))
    
    def vector_magnitude(self, data: List[Union[int, float]]) -> float:
        """Calculate vector magnitude using Zig backend."""
        if not data:
            return 0.0
        
        float_array = self._to_float_array(data)
        return self._lib.zig_vector_magnitude_f64(float_array, len(data))
    
    def batch_statistics(self, data: List[Union[int, float]]) -> dict:
        """Calculate multiple statistics in one FFI call."""
        if not data:
            return {'sum': 0.0, 'mean': 0.0, 'min': 0.0, 'max': 0.0, 'stdev': 0.0}
        
        float_array = self._to_float_array(data)
        results = (ctypes.c_double * 5)()  # 5 results
        self._lib.zig_batch_stats_f64(float_array, len(data), results)
        
        return {
            'sum': results[0],
            'mean': results[1],
            'min': results[2],
            'max': results[3],
            'stdev': results[4]
        }
    
    def batch_basic(self, data: List[Union[int, float]]) -> dict:
        """Calculate basic statistics in one FFI call."""
        if not data:
            return {'sum': 0.0, 'mean': 0.0, 'min': 0.0, 'max': 0.0}
        
        float_array = self._to_float_array(data)
        results = (ctypes.c_double * 4)()  # 4 results
        self._lib.zig_batch_basic_f64(float_array, len(data), results)
        
        return {
            'sum': results[0],
            'mean': results[1],
            'min': results[2],
            'max': results[3]
        }