"""
C++ backend interface for PyFunc operations.
"""

from typing import Any, Callable, Generator, Optional, Union, List
from collections.abc import Iterable
from ..placeholder import Placeholder
from ..errors import PipelineError

def is_cpp_available() -> bool:
    """Check if C++ backend is available."""
    try:
        import pyfunc_native  # This will be our compiled C++ module
        return True
    except ImportError:
        return False

class CppBackend:
    """C++ backend for high-performance operations."""
    
    def __init__(self):
        try:
            import pyfunc_native
            self._native = pyfunc_native
            self._available = True
        except ImportError:
            self._native = None
            self._available = False
            raise ImportError("C++ backend not available. Install with: pip install pyfunc-pipeline[cpp]")
    
    def supports_operation(self, operation: str, func: Any = None) -> bool:
        """Check if operation is supported by C++ backend."""
        if not self._available:
            return False
        
        supported_ops = {'map', 'filter', 'reduce', 'sum', 'min', 'max', 'count'}
        if operation not in supported_ops:
            return False
        
        # For operations with functions, check if we can compile them
        if func is not None and operation in {'map', 'filter', 'reduce'}:
            return self._can_compile_function(func)
        
        return True
    
    def supports_data_type(self, data: Any) -> bool:
        """Check if data type is supported by C++ backend."""
        if not self._available:
            return False
        
        # Support numeric iterables
        if isinstance(data, (list, tuple)):
            if not data:  # Empty
                return True
            # Check if all elements are numeric
            return all(isinstance(x, (int, float)) for x in data)
        
        return False
    
    def _can_compile_function(self, func: Any) -> bool:
        """Check if function can be compiled to C++."""
        if isinstance(func, Placeholder):
            # Check if placeholder represents a simple operation
            return self._is_simple_placeholder(func)
        
        # For now, only support placeholders
        return False
    
    def _is_simple_placeholder(self, placeholder: Placeholder) -> bool:
        """Check if placeholder represents a simple arithmetic operation."""
        # This is a simplified check - in reality, we'd analyze the operation tree
        # For now, assume simple binary operations are supported
        return hasattr(placeholder, '_op_func') and placeholder._op_func is not None
    
    def _compile_placeholder(self, placeholder: Placeholder) -> str:
        """Convert placeholder to C++ operation code."""
        if not isinstance(placeholder, Placeholder):
            raise PipelineError("Can only compile Placeholder objects")
        
        # Check if this is a binary operation placeholder
        if hasattr(placeholder, '_op_func') and placeholder._op_func is not None:
            op_func = placeholder._op_func
            other = placeholder._other_operand
            
            # Test the operation with sample values to determine the type
            try:
                # Test with sample values to identify the operation
                test_result_1 = op_func(10, 5)
                test_result_2 = op_func(0, 1)
                
                # Identify operation by testing results
                if op_func(5, 3) == 8:  # Addition
                    return f"add_{other}"
                elif op_func(5, 3) == 2:  # Subtraction
                    return f"sub_{other}"
                elif op_func(5, 3) == 15:  # Multiplication
                    return f"mul_{other}"
                elif op_func(6, 3) == 2:  # Division
                    return f"div_{other}"
                elif op_func(5, 3) == True:  # Greater than
                    return f"gt_{other}"
                elif op_func(3, 5) == True:  # Less than
                    return f"lt_{other}"
                elif op_func(5, 5) == True:  # Greater than or equal
                    return f"ge_{other}"
                elif op_func(3, 3) == True:  # Less than or equal
                    return f"le_{other}"
                elif op_func(5, 5) == True and op_func(5, 3) == False:  # Equal
                    return f"eq_{other}"
                elif op_func(5, 3) == True and op_func(5, 5) == False:  # Not equal
                    return f"ne_{other}"
            except:
                pass
            
            # Fallback: try to analyze the lambda source if possible
            import inspect
            try:
                source = inspect.getsource(op_func)
                if '+' in source:
                    return f"add_{other}"
                elif '*' in source:
                    return f"mul_{other}"
                elif '>' in source and '=' not in source:
                    return f"gt_{other}"
                elif '<' in source and '=' not in source:
                    return f"lt_{other}"
                elif '>=' in source:
                    return f"ge_{other}"
                elif '<=' in source:
                    return f"le_{other}"
                elif '==' in source:
                    return f"eq_{other}"
                elif '!=' in source:
                    return f"ne_{other}"
                elif '-' in source:
                    return f"sub_{other}"
                elif '/' in source:
                    return f"div_{other}"
            except:
                pass
        
        return "identity"  # Fallback
    
    def map(self, data: Any, func: Callable) -> Generator[Any, None, None]:
        """Map function over data using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        if isinstance(func, Placeholder):
            op_code = self._compile_placeholder(func)
            # Convert to list for C++ processing
            data_list = list(data) if not isinstance(data, list) else data
            
            # Determine if input data is all integers
            all_ints = all(isinstance(x, int) for x in data_list)
            
            # Call C++ implementation
            result = self._native.map_operation(data_list, op_code)
            
            # Convert back to appropriate types
            for item in result:
                if all_ints and item.is_integer():
                    yield int(item)
                else:
                    yield item
        else:
            raise PipelineError("C++ backend currently only supports Placeholder functions")
    
    def filter(self, data: Any, predicate: Callable) -> Generator[Any, None, None]:
        """Filter data using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        if isinstance(predicate, Placeholder):
            op_code = self._compile_placeholder(predicate)
            data_list = list(data) if not isinstance(data, list) else data
            
            # Determine if input data is all integers
            all_ints = all(isinstance(x, int) for x in data_list)
            
            result = self._native.filter_operation(data_list, op_code)
            
            # Convert back to appropriate types
            for item in result:
                if all_ints and item.is_integer():
                    yield int(item)
                else:
                    yield item
        else:
            raise PipelineError("C++ backend currently only supports Placeholder predicates")
    
    def reduce(self, data: Any, func: Callable, initializer: Optional[Any] = None) -> Any:
        """Reduce data using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        if isinstance(func, Placeholder):
            op_code = self._compile_placeholder(func)
            data_list = list(data) if not isinstance(data, list) else data
            
            if initializer is None:
                return self._native.reduce_operation(data_list, op_code)
            else:
                return self._native.reduce_operation_with_init(data_list, op_code, initializer)
        else:
            raise PipelineError("C++ backend currently only supports Placeholder functions")
    
    def sum(self, data: Any) -> Union[int, float]:
        """Sum data using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        data_list = list(data) if not isinstance(data, list) else data
        
        # Determine if input data is all integers
        all_ints = all(isinstance(x, int) for x in data_list)
        
        result = self._native.sum_operation(data_list)
        
        # Convert back to int if input was all ints and result is a whole number
        if all_ints and result.is_integer():
            return int(result)
        return result
    
    def min(self, data: Any) -> Union[int, float]:
        """Find minimum using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        data_list = list(data) if not isinstance(data, list) else data
        return self._native.min_operation(data_list)
    
    def max(self, data: Any) -> Union[int, float]:
        """Find maximum using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        data_list = list(data) if not isinstance(data, list) else data
        return self._native.max_operation(data_list)
    
    def count(self, data: Any) -> int:
        """Count elements using C++ backend."""
        if not self._available:
            raise PipelineError("C++ backend not available")
        
        data_list = list(data) if not isinstance(data, list) else data
        return self._native.count_operation(data_list)