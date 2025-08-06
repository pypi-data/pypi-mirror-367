"""
Python backend implementation - the original PyFunc logic.
"""

from typing import Any, Callable, Generator, Optional, Union
from collections.abc import Iterable
from ..placeholder import Placeholder
from ..errors import PipelineError

class PythonBackend:
    """Original Python implementation of PyFunc operations."""
    
    def _unwrap(self, func: Any) -> Callable[[Any], Any]:
        """Unwrap a function or placeholder into an executable callable."""
        if isinstance(func, Placeholder):
            return func._func
        elif callable(func):
            return func
        else:
            raise PipelineError("Provided object is not callable or a valid placeholder.")
    
    def map(self, data: Any, func: Callable) -> Generator[Any, None, None]:
        """Map function over data."""
        executable = self._unwrap(func)
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            for item in data:
                yield executable(item)
        else:
            yield executable(data)
    
    def filter(self, data: Any, predicate: Callable) -> Generator[Any, None, None]:
        """Filter data based on predicate."""
        executable = self._unwrap(predicate)
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            for item in data:
                if executable(item):
                    yield item
        else:
            raise PipelineError("filter() can only be used on iterables (excluding str/bytes).")
    
    def reduce(self, data: Any, func: Callable, initializer: Optional[Any] = None) -> Any:
        """Reduce data using function."""
        from functools import reduce as py_reduce
        
        executable = self._unwrap(func) if not isinstance(func, Placeholder) else func.as_reducer()
        
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            if initializer is None:
                return py_reduce(executable, data)
            else:
                return py_reduce(executable, data, initializer)
        else:
            raise PipelineError("reduce() can only be used on iterables (excluding str/bytes).")
    
    def sum(self, data: Any) -> Union[int, float]:
        """Sum numeric data."""
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            return sum(data)
        else:
            raise PipelineError("sum() can only be used on iterables (excluding str/bytes).")
    
    def min(self, data: Any) -> Any:
        """Find minimum value."""
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            try:
                return min(data)
            except ValueError:
                return None
        else:
            raise PipelineError("min() can only be used on iterables (excluding str/bytes).")
    
    def max(self, data: Any) -> Any:
        """Find maximum value."""
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            try:
                return max(data)
            except ValueError:
                return None
        else:
            raise PipelineError("max() can only be used on iterables (excluding str/bytes).")
    
    def count(self, data: Any) -> int:
        """Count elements."""
        if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            return sum(1 for _ in data)
        else:
            raise PipelineError("count() can only be used on iterables (excluding str/bytes).")