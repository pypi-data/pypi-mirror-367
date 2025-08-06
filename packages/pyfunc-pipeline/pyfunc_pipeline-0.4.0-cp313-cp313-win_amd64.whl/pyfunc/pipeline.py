from collections.abc import Iterable, Callable, Generator
import copy
from functools import reduce
import itertools
import os
from typing import TypeVar, Generic, Any, Optional, cast, Union

from .errors import PipelineError
from .placeholder import Placeholder
from .backends import get_backend
from .statistics import median, stdev
from . import bitwise as python_bitwise

# Conditional import for C++ backend
if os.environ.get('PYFUNC_BUILD_CPP', '1') == '1':
    try:
        from . import native_c
    except ImportError:
        native_c = None # Set to None if not available

# Conditional import for Go backend
if os.environ.get('PYFUNC_BUILD_GO', '0') == '1':  # Temporarily disabled
    try:
        from . import native_go
    except ImportError:
        native_go = None # Set to None if not available
else:
    native_go = None

# Define a TypeVar for the value in the Pipeline
T = TypeVar('T')
U = TypeVar('U')

# ======================================================================
# The Complete and Corrected Pipeline Class
# ======================================================================

class Pipeline(Generic[T]):
    """
    A chainable functional pipeline for transforming values or iterables.
    Supports chaining, conditional application, operator overloading, and more.
    """
    _custom_type_handlers: dict[type, dict[str, Callable[[Any], Any]]] = {}

    @classmethod
    def register_custom_type(cls, custom_type: type, handlers: dict[str, Callable[[Any], Any]]) -> None:
        """Register custom type handlers for specific operations."""
        cls._custom_type_handlers[custom_type] = handlers

    @classmethod
    def extend(cls, name: str, func: Callable[..., Any]) -> None:
        """Extend the Pipeline class with a new method."""
        setattr(cls, name, func)

    @classmethod
    def from_iterable(cls, iterable: Iterable[T]) -> 'Pipeline[Generator[T, None, None]]':
        """Create a Pipeline from any iterable (tuple, set, generator, etc)."""
        return cast('Pipeline[Generator[T, None, None]]', cls(initial_value=iter(iterable)))

    def __init__(self, initial_value: Any = None, _pipeline_func: Optional[Callable[[Any], Any]] = None):
        # _initial_value is the starting value for the pipeline when .get() is called
        self._initial_value = initial_value
        # _pipeline_func is the accumulated function representing all chained operations
        self._pipeline_func: Callable[[Any], Any] = _pipeline_func if _pipeline_func is not None else (lambda x: x)

    def __repr__(self) -> str:
        """Representation for easier debugging."""
        return f"Pipeline(initial_value={repr(self._initial_value)}, func={self._pipeline_func.__name__ if hasattr(self._pipeline_func, '__name__') else 'lambda'})"

    def get(self) -> Any:
        """Get the current value from the pipeline by applying all accumulated functions."""
        return self._pipeline_func(self._initial_value)

    def clone(self) -> 'Pipeline[T]':
        """Return a new Pipeline with the same initial value and accumulated function."""
        return Pipeline(copy.deepcopy(self._initial_value), self._pipeline_func)

    # --- Core Methods ---

    def apply(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Apply func to the value (or map over iterable). Chainable."""
        executable = self._unwrap(func)
        new_pipeline_func = lambda x: executable(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def then(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Alias for apply method for chaining operations."""
        return self.apply(func)

    def map(self, func: Callable[[Any], U]) -> 'Pipeline[Generator[U, None, None]]':
        """Map a function over elements with optional C++ acceleration."""
        def _map_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val, 'map', func):
                        yield from backend.execute_map(val, func)
                        return
                except Exception:
                    # Fall back to Python if C++ fails
                    pass
                
                # Python implementation
                executable = self._unwrap(func)
                yield from (executable(v) for v in val)
            else:
                executable = self._unwrap(func)
                yield executable(val)
        new_pipeline_func = lambda x: _map_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def map_cpp(self, func: Callable[[Any], U]) -> 'Pipeline[Generator[U, None, None]]':
        """Map a function over elements using C++ backend explicitly."""
        def _map_cpp_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                
                if not native_c.supports_operation('map', func):
                    raise PipelineError(f"C++ backend doesn't support this map operation: {func}")
                
                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    yield from native_c.map(val_list, func)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("map_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _map_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def pipe(self, *funcs: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Applies a sequence of functions to the current value in order."""
        def chained_func(x: Any) -> Any:
            result = x
            for f in funcs:
                executable = self._unwrap(f)
                result = executable(result)
            return result
        new_pipeline_func = lambda x: chained_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def compose(self, *funcs: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Compose multiple functions and apply them as a single transformation."""
        composed = reduce(lambda f, g: lambda x: self._unwrap(f)(self._unwrap(g)(x)), reversed(funcs))
        new_pipeline_func = lambda x: composed(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reduce(self, func: Callable[[Any, Any], U], initializer: Optional[Any] = None) -> 'Pipeline[U]':
        """Apply a function of two arguments cumulatively to the items of an iterable, from left to right, to reduce the iterable to a single value."""
        def _reduce_func(val: Any) -> U:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert generators/iterators to lists to allow reuse and size checking
                val_list = list(val)
                
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val_list, 'reduce', func):
                        return backend.execute_reduce(val_list, func, initializer)
                except Exception:
                    # Fall back to Python if C++ fails
                    pass

                # Python implementation
                executable: Callable[[Any, Any], Any]
                if isinstance(func, Placeholder):
                    executable = func.as_reducer()
                else:
                    executable = func
                
                if initializer is None:
                    return reduce(executable, val_list)
                else:
                    return reduce(executable, val_list, initializer)
            else:
                raise PipelineError("reduce() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reduce_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reduce_cpp(self, func: Callable[[Any, Any], U], initializer: Optional[Any] = None) -> 'Pipeline[U]':
        """Reduce elements using C++ backend explicitly."""
        def _reduce_cpp_func(val: Any) -> U:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")

                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val

                if not native_c.supports_operation('reduce', func):
                    raise PipelineError(f"C++ backend doesn't support this reduce operation: {func}")

                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")

                try:
                    return native_c.reduce(val_list, func, initializer)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("reduce_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _reduce_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reduce_right(self, func: Callable[[Any, Any], U], initializer: Optional[Any] = None) -> 'Pipeline[U]':
        """Apply a function of two arguments cumulatively to the items of an iterable, from right to left, to reduce the iterable to a single value."""
        executable: Callable[[Any, Any], Any]
        if isinstance(func, Placeholder):
            executable = func.as_reducer()
        else:
            executable = func # If not a Placeholder, assume it's a regular 2-arg function

        def _reduce_right_func(val: Any) -> U:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert to list to allow reverse iteration and indexing
                val_list = list(val)
                if initializer is None:
                    # If no initializer, start with the last element
                    if not val_list:
                        raise TypeError("reduce_right() of empty sequence with no initial value")
                    acc = val_list[-1]
                    items: Iterable[Any] = val_list[-2::-1] # Iterate from second to last to first
                else:
                    acc = initializer
                    items = reversed(val_list) # Iterate from last to first

                for item in items:
                    acc = executable(item, acc) # Note: item, acc for right-to-left
                return acc
            else:
                raise PipelineError("reduce_right() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reduce_right_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Conditional Application ---

    def apply_if(self, condition: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply func to the entire value if condition is True (or condition(self.value) is True if callable)."""
        executable_condition = self._unwrap(condition)
        executable_func = self._unwrap(func)
        def _apply_if_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_condition(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _apply_if_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def when(self, pred: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `func` only if `pred(value)` is True."""
        executable_pred = self._unwrap(pred)
        executable_func = self._unwrap(func)
        def _when_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_pred(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _when_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def unless(self, pred: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `func` only if `pred(value)` is False."""
        executable_pred = self._unwrap(pred)
        executable_func = self._unwrap(func)
        def _unless_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if not executable_pred(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _unless_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def if_else(self, pred: Callable[[Any], bool], then_fn: Callable[[Any], Any], else_fn: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `then_fn` if `pred(value)` is True, otherwise apply `else_fn`."""
        executable_pred = self._unwrap(pred)
        executable_then_fn = self._unwrap(then_fn)
        executable_else_fn = self._unwrap(else_fn)
        def _if_else_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_pred(processed_val):
                return executable_then_fn(processed_val)
            else:
                return executable_else_fn(processed_val)
        new_pipeline_func = lambda x: _if_else_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Operator Overloads ---

    def __or__(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Allow using | operator for chaining: Pipeline(42) | square | half"""
        return self.apply(func)

    def __rshift__(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Allow using >> operator for chaining: Pipeline(42) >> square >> half"""
        return self.apply(func)

    # --- Iterable Manipulation ---
    
    def pairwise(self) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Group elements of a list into pairs as tuples."""
        def _pairwise_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, list):
                for i in range(0, len(val) - 1, 2):
                    yield (val[i], val[i + 1])
            else:
                raise PipelineError("pairwise() can only be used on lists.")
        new_pipeline_func = lambda x: _pairwise_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)
        
    def filter(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Filter elements of an iterable based on a predicate with optional C++ acceleration."""
        def _filter_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val, 'filter', predicate):
                        yield from backend.execute_filter(val, predicate)
                        return
                except Exception:
                    # Fall back to Python if C++ fails
                    pass
                
                # Python implementation
                executable = self._unwrap(predicate)
                for v in val:
                    if executable(v):
                        yield v
            else:
                raise PipelineError("filter() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _filter_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def filter_cpp(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Filter elements using C++ backend explicitly."""
        def _filter_cpp_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.cpp_backend is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                
                if not backend.cpp_backend.supports_operation('filter', predicate):
                    raise PipelineError(f"C++ backend doesn't support this filter operation: {predicate}")
                
                if not backend.cpp_backend.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    yield from backend.cpp_backend.filter(val_list, predicate)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("filter_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _filter_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def flatten(self) -> 'Pipeline[Generator[Any, None, None]]':
        """Flatten one level of nested iterables."""
        def _flatten_func(val: Any) -> Generator[Any, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for item in val:
                    if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                        yield from item
                    else:
                        yield item
            else:
                raise PipelineError("flatten() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _flatten_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def flatten_deep(self) -> 'Pipeline[Generator[Any, None, None]]':
        """Recursively flatten nested iterables."""
        def _flatten_deep_func(val: Any) -> Generator[Any, None, None]:
            def _flatten(v: Any) -> Generator[Any, None, None]:
                for i in v:
                    if isinstance(i, Iterable) and not isinstance(i, (str, bytes)):
                        yield from _flatten(i)
                    else:
                        yield i
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from _flatten(val)
            else:
                raise PipelineError("flatten_deep() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _flatten_deep_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def chunk(self, size: int) -> 'Pipeline[Generator[list[T], None, None]]':
        """Break a sequence into chunks of the given size."""
        def _chunk_func(val: Any) -> Generator[list[T], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(0, len(val), size):
                    yield val[i:i + size]
            else:
                raise PipelineError("chunk() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _chunk_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def window(self, size: int, step: int = 1) -> 'Pipeline[Generator[list[T], None, None]]':
        """Create a sliding window view over a sequence."""
        def _window_func(val: Any) -> Generator[list[T], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(0, len(val) - size + 1, step):
                    yield val[i:i + size]
            else:
                raise PipelineError("window() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _window_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sliding_reduce(self, func: Callable[[Any], U], size: int) -> 'Pipeline[Generator[U, None, None]]':
        """Create sliding windows and apply a function to each."""
        executable_func = self._unwrap(func)
        def _sliding_reduce_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(len(val) - size + 1):
                    yield executable_func(val[i:i + size])
            else:
                raise PipelineError("sliding_reduce() can only be used on iterables.")
        new_pipeline_func = lambda x: _sliding_reduce_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sliding_pairs(self) -> 'Pipeline[Generator[list[T], None, None]]':
        """Create a sliding window of pairs over a sequence."""
        return self.window(2, 1)

    def sort(self, key: Optional[Callable[[Any], Any]] = None, reverse: bool = False) -> 'Pipeline[list[T]]':
        """Sort the iterable."""
        executable_key = self._unwrap(key) if key else None
        def _sort_func(val: Any) -> list[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return sorted(val, key=executable_key, reverse=reverse)
            else:
                raise PipelineError("sort() can only be used on iterables.")
        new_pipeline_func = lambda x: _sort_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def unique(self) -> 'Pipeline[Generator[T, None, None]]':
        """Remove duplicates from the iterable while preserving order."""
        def _unique_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                seen = set()
                for x in val:
                    if x not in seen:
                        seen.add(x)
                        yield x
            else:
                raise PipelineError("unique() can only be used on iterables.")
        new_pipeline_func = lambda x: _unique_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def starmap(self, func: Callable[..., U]) -> 'Pipeline[Generator[U, None, None]]':
        """Apply a function to each tuple in a list of tuples."""
        executable = self._unwrap(func)
        def _starmap_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i in val:
                    if isinstance(i, tuple):
                        yield executable(*i)
                    else:
                        raise PipelineError("starmap() can only be used on iterables of tuples.")
            else:
                raise PipelineError("starmap() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _starmap_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def first(self) -> 'Pipeline[Optional[T]]':
        """Get the first element of an iterable."""
        def _first_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return next(iter(val), None)
            else:
                raise PipelineError("first() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _first_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def last(self) -> 'Pipeline[Optional[T]]':
        """Get the last element of an iterable."""
        def _last_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    if isinstance(val, list): # Optimize for lists
                        return val[-1]
                    # For other iterables, consume to get the last element
                    last_item = None
                    for item in val:
                        last_item = item
                    return last_item
                except IndexError:
                    return None
            else:
                raise PipelineError("last() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _last_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def nth(self, n: int) -> 'Pipeline[Optional[T]]':
        """Get the nth element of an iterable (0-indexed)."""
        def _nth_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    if isinstance(val, list):
                        return val[n]
                    # For other iterables, iterate to the nth element
                    for i, item in enumerate(val):
                        if i == n:
                            return item
                    return None # n is out of bounds
                except IndexError:
                    return None
            else:
                raise PipelineError("nth() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _nth_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def is_empty(self) -> 'Pipeline[bool]':
        """Check if the iterable is empty."""
        def _is_empty_func(val: Any) -> bool:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return not bool(list(val)) # Convert to list to check emptiness
            else:
                raise PipelineError("is_empty() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _is_empty_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def count(self) -> 'Pipeline[int]':
        """Count the number of elements in an iterable with optional C++ acceleration."""
        def _count_func(val: Any) -> int:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert generators/iterators to lists to allow reuse and size checking
                val_list = list(val)
                
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val_list, 'count'):
                        return backend.execute_sum(val_list)
                except Exception:
                    # Fall back to Python if C++ fails
                    pass
                
                # Python implementation
                return len(val_list)
            else:
                raise PipelineError("count() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _count_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def count_cpp(self) -> 'Pipeline[int]':
        """Count the number of elements in an iterable using C++ backend explicitly."""
        def _count_cpp_func(val: Any) -> int:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                
                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return native_c.count(val_list)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("count_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _count_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sum(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the sum of elements in an iterable with optional backend acceleration."""
        def _sum_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val_list = list(val)
                backend = get_backend()
                
                # Try Zig backend for mathematical operations
                try:
                    if backend.should_use_zig(val_list, 'sum') and backend.zig_backend:
                        return backend.zig_backend.sum(val_list)
                except Exception:
                    pass
                
                # Try C++ backend
                try:
                    if backend.should_use_cpp(val_list, 'sum'):
                        return backend.execute_sum(val_list)
                except Exception:
                    pass
                
                # Python implementation
                return sum(val_list)
            else:
                raise PipelineError("sum() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _sum_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sum_cpp(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the sum using C++ backend explicitly."""
        def _sum_cpp_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                
                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return native_c.sum(val_list)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("sum_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _sum_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def min(self) -> 'Pipeline[Optional[T]]':
        """Get the minimum element in an iterable with optional C++ acceleration."""
        def _min_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert generators/iterators to lists to allow reuse and size checking
                val_list = list(val)
                if not val_list:
                    return None
                
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val_list, 'min'):
                        return backend.cpp_backend.min(val_list)
                except Exception:
                    # Fall back to Python if C++ fails
                    pass
                
                # Python implementation
                return min(val_list)
            else:
                raise PipelineError("min() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _min_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def min_cpp(self) -> 'Pipeline[Optional[T]]':
        """Get the minimum element in an iterable using C++ backend explicitly."""
        def _min_cpp_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                if not val_list:
                    return None
                
                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return native_c.min(val_list)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("min_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _min_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def max(self) -> 'Pipeline[Optional[T]]':
        """Get the maximum element in an iterable with optional C++ acceleration."""
        def _max_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert generators/iterators to lists to allow reuse and size checking
                val_list = list(val)
                if not val_list:
                    return None
                
                # Try C++ backend for supported operations
                backend = get_backend()
                try:
                    if backend.should_use_cpp(val_list, 'max'):
                        return backend.cpp_backend.max(val_list)
                except Exception:
                    # Fall back to Python if C++ fails
                    pass
                
                # Python implementation
                return max(val_list)
            else:
                raise PipelineError("max() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _max_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def max_cpp(self) -> 'Pipeline[Optional[T]]':
        """Get the maximum element in an iterable using C++ backend explicitly."""
        def _max_cpp_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if native_c is None:
                    raise PipelineError("C++ backend not available")
                
                # Convert to list if it's a generator
                val_list = list(val) if hasattr(val, '__iter__') and not isinstance(val, (list, tuple)) else val
                if not val_list:
                    return None
                
                if not native_c.supports_data_type(val_list):
                    raise PipelineError(f"C++ backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return native_c.max(val_list)
                except Exception as e:
                    raise PipelineError(f"C++ backend failed: {e}")
            else:
                raise PipelineError("max_cpp() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _max_cpp_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Statistical Methods ---

    def median(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the median of the elements in an iterable with optional Rust acceleration."""
        def _median_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val_list = list(val)
                
                # Try Rust backend for large datasets (configurable threshold)
                backend = get_backend()
                if backend.should_use_rust(val_list, 'median'):
                    try:
                        if backend.rust_backend is not None:
                            return backend.rust_backend.median(val_list)
                    except Exception:
                        pass  # Fall back to Python
                
                # Python implementation for small datasets or when Rust unavailable
                return median(val_list)
            else:
                raise PipelineError("median() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _median_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def stdev(self) -> 'Pipeline[float]':
        """Calculate the standard deviation of the elements in an iterable with optional Rust acceleration."""
        def _stdev_func(val: Any) -> float:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val_list = list(val)
                
                # Try Rust backend for large datasets (configurable threshold)
                backend = get_backend()
                if backend.should_use_rust(val_list, 'stdev'):
                    try:
                        if backend.rust_backend is not None:
                            return backend.rust_backend.stdev(val_list)
                    except Exception:
                        pass  # Fall back to Python
                
                # Python implementation for small datasets or when Rust unavailable
                return stdev(val_list)
            else:
                raise PipelineError("stdev() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _stdev_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def median_rust(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the median using Rust backend explicitly."""
        def _median_rust_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.rust_backend is None:
                    raise PipelineError("Rust backend not available")
                
                val_list = list(val)
                if not backend.rust_backend.supports_data_type(val_list):
                    raise PipelineError(f"Rust backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return backend.rust_backend.median(val_list)
                except Exception as e:
                    raise PipelineError(f"Rust backend failed: {e}")
            else:
                raise PipelineError("median_rust() can only be used on iterables (excluding str/bytes)")
        
        new_pipeline_func = lambda x: _median_rust_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def stdev_rust(self) -> 'Pipeline[float]':
        """Calculate the standard deviation using Rust backend explicitly."""
        def _stdev_rust_func(val: Any) -> float:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.rust_backend is None:
                    raise PipelineError("Rust backend not available")
                
                val_list = list(val)
                if not backend.rust_backend.supports_data_type(val_list):
                    raise PipelineError(f"Rust backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return backend.rust_backend.stdev(val_list)
                except Exception as e:
                    raise PipelineError(f"Rust backend failed: {e}")
            else:
                raise PipelineError("stdev_rust() can only be used on iterables (excluding str/bytes)")
        
        new_pipeline_func = lambda x: _stdev_rust_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sum_zig(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the sum using Zig backend explicitly."""
        def _sum_zig_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.zig_backend is None:
                    raise PipelineError("Zig backend not available")
                
                val_list = list(val)
                if not backend.zig_backend.supports_data_type(val_list):
                    raise PipelineError(f"Zig backend doesn't support this data type: {type(val_list)}")
                
                try:
                    return backend.zig_backend.sum(val_list)
                except Exception as e:
                    raise PipelineError(f"Zig backend failed: {e}")
            else:
                raise PipelineError("sum_zig() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _sum_zig_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def mean_zig(self) -> 'Pipeline[float]':
        """Calculate the mean using Zig backend explicitly."""
        def _mean_zig_func(val: Any) -> float:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.zig_backend is None:
                    raise PipelineError("Zig backend not available")
                
                val_list = list(val)
                try:
                    return backend.zig_backend.mean(val_list)
                except Exception as e:
                    raise PipelineError(f"Zig backend failed: {e}")
            else:
                raise PipelineError("mean_zig() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _mean_zig_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def stdev_zig(self) -> 'Pipeline[float]':
        """Calculate the standard deviation using Zig backend explicitly."""
        def _stdev_zig_func(val: Any) -> float:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.zig_backend is None:
                    raise PipelineError("Zig backend not available")
                
                val_list = list(val)
                try:
                    return backend.zig_backend.stdev(val_list)
                except Exception as e:
                    raise PipelineError(f"Zig backend failed: {e}")
            else:
                raise PipelineError("stdev_zig() can only be used on iterables (excluding str/bytes)")
        new_pipeline_func = lambda x: _stdev_zig_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Bitwise Methods ---

    def bitwise_and(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise AND on each element in an iterable with optional Go acceleration."""
        def _bitwise_and_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val_list = list(val)
                backend = get_backend()
                
                # Try Go backend for bitwise operations
                try:
                    if backend.should_use_go(val_list, 'bitwise_and') and backend.go_backend:
                        yield from backend.go_backend.bitwise_and(val_list, operand)
                        return
                except Exception:
                    pass
                
                # Python implementation fallback
                yield from python_bitwise.bitwise_and(val_list, operand)
            else:
                raise PipelineError("bitwise_and() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _bitwise_and_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def bitwise_or(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise OR on each element in an iterable."""
        def _bitwise_or_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from python_bitwise.bitwise_or(val, operand)
            else:
                raise PipelineError("bitwise_or() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _bitwise_or_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def bitwise_xor(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise XOR on each element in an iterable."""
        def _bitwise_xor_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from python_bitwise.bitwise_xor(val, operand)
            else:
                raise PipelineError("bitwise_xor() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _bitwise_xor_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def bitwise_not(self) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise NOT on each element in an iterable."""
        def _bitwise_not_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from python_bitwise.bitwise_not(val)
            else:
                raise PipelineError("bitwise_not() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _bitwise_not_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def left_shift(self, bits: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise left shift on each element in an iterable."""
        def _left_shift_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from python_bitwise.left_shift(val, bits)
            else:
                raise PipelineError("left_shift() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _left_shift_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def right_shift(self, bits: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise right shift on each element in an iterable."""
        def _right_shift_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from python_bitwise.right_shift(val, bits)
            else:
                raise PipelineError("right_shift() can only be used on iterables of integers.")
        new_pipeline_func = lambda x: _right_shift_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def bitwise_and_go(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise AND using Go backend explicitly."""
        def _bitwise_and_go_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.go_backend is None:
                    raise PipelineError("Go backend not available")
                
                val_list = list(val)
                try:
                    yield from backend.go_backend.bitwise_and(val_list, operand)
                except Exception as e:
                    raise PipelineError(f"Go backend failed: {e}")
            else:
                raise PipelineError("bitwise_and_go() can only be used on iterables of integers")
        new_pipeline_func = lambda x: _bitwise_and_go_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def bitwise_or_go(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
        """Perform a bitwise OR using Go backend explicitly."""
        def _bitwise_or_go_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                backend = get_backend()
                if backend.go_backend is None:
                    raise PipelineError("Go backend not available")
                
                val_list = list(val)
                try:
                    yield from backend.go_backend.bitwise_or(val_list, operand)
                except Exception as e:
                    raise PipelineError(f"Go backend failed: {e}")
            else:
                raise PipelineError("bitwise_or_go() can only be used on iterables of integers")
        new_pipeline_func = lambda x: _bitwise_or_go_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reverse(self) -> 'Pipeline[list[T]]':
        """Reverse the order of elements in an iterable."""
        def _reverse_func(val: Any) -> list[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return list(reversed(val))
            else:
                raise PipelineError("reverse() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reverse_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def take(self, n: int) -> 'Pipeline[Generator[T, None, None]]':
        """Take the first n elements from the iterable."""
        def _take_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i, item in enumerate(val):
                    if i < n:
                        yield item
                    else:
                        break
            else:
                raise PipelineError("take() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _take_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def take_while(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Take elements from the iterable as long as the predicate is true."""
        executable_predicate = self._unwrap(predicate)
        def _take_while_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for item in val:
                    if executable_predicate(item):
                        yield item
                    else:
                        break
            else:
                raise PipelineError("take_while() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _take_while_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def skip(self, n: int) -> 'Pipeline[Generator[T, None, None]]':
        """Skip the first n elements from the iterable."""
        def _skip_func(val: Any) -> Generator[int, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i, item in enumerate(val):
                    if i >= n:
                        yield item
            else:
                raise PipelineError("skip() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _skip_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def skip_while(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Skip elements from the iterable as long as the predicate is true."""
        executable_predicate = self._unwrap(predicate)
        def _skip_while_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                skipping = True
                for item in val:
                    if skipping and executable_predicate(item):
                        continue
                    else:
                        skipping = False
                        yield item
            else:
                raise PipelineError("skip_while() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _skip_while_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def chain(self, *others: Iterable[Any]) -> 'Pipeline[Generator[Any, None, None]]':
        """Concatenate multiple sequences."""
        def _chain_func(val: Any) -> Generator[Any, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from val
                for other_val in others:
                    if isinstance(other_val, Iterable) and not isinstance(other_val, (str, bytes)):
                        yield from other_val
                    else:
                        raise PipelineError("chain() can only concatenate iterables (excluding str/bytes).")
            else:
                raise PipelineError("chain() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _chain_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def zip_with(self, other: Iterable[Any]) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Zip the current iterable with another iterable."""
        def _zip_with_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, Iterable) and isinstance(other, Iterable):
                yield from zip(val, other)
            else:
                raise PipelineError("zip_with() requires two iterables.")
        new_pipeline_func = lambda x: _zip_with_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def product(self, *iterables: Iterable[Any]) -> 'Pipeline[Generator[tuple[Any, ...], None, None]]':
        """Cartesian product of input iterables."""
        def _product_func(val: Any) -> Generator[tuple[Any, ...], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from itertools.product(val, *iterables)
            else:
                raise PipelineError("product() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _product_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def combinations(self, r: int) -> 'Pipeline[Generator[tuple[Any, ...], None, None]]':
        """Return r-length subsequences of elements from the input iterable."""
        def _combinations_func(val: Any) -> Generator[tuple[Any, ...], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from itertools.combinations(val, r)
            else:
                raise PipelineError("combinations() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _combinations_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def group_by(self, key: Callable[[Any], Any]) -> 'Pipeline[dict[Any, list[T]]]':
        """Group elements of an iterable based on a key function."""
        executable_key = self._unwrap(key)
        def _group_by_func(val: Any) -> dict[Any, list[T]]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                groups: dict[Any, list[T]] = {}
                for item in val:
                    group_key = executable_key(item)
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append(item)
                return groups
            else:
                raise PipelineError("group_by() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _group_by_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Conversion Methods ---

    def to_list(self) -> list[Any]:
        """Convert the pipeline result to a list."""
        result = self.get()
        if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
            return list(result)
        else:
            return [result]

    # --- String Methods ---

    def explode(self, delimiter: Optional[str] = None) -> 'Pipeline[Generator[str, None, None]]':
        """Split a string into characters or words."""
        def _explode_func(val: Any) -> Generator[str, None, None]:
            if isinstance(val, str):
                if delimiter is None:
                    # Split into characters
                    yield from val
                else:
                    # Split by delimiter
                    yield from val.split(delimiter)
            else:
                raise PipelineError("explode() can only be used on strings.")
        new_pipeline_func = lambda x: _explode_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def implode(self, separator: str = "") -> 'Pipeline[str]':
        """Join an iterable of strings into a single string."""
        def _implode_func(val: Any) -> str:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return separator.join(str(item) for item in val)
            else:
                raise PipelineError("implode() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _implode_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def surround(self, prefix: str, suffix: str) -> 'Pipeline[str]':
        """Surround a string with prefix and suffix."""
        def _surround_func(val: Any) -> str:
            if isinstance(val, str):
                return f"{prefix}{val}{suffix}"
            else:
                raise PipelineError("surround() can only be used on strings.")
        new_pipeline_func = lambda x: _surround_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def template_fill(self, values: dict[str, Any]) -> 'Pipeline[str]':
        """Fill a template string with values using format()."""
        def _template_fill_func(val: Any) -> str:
            if isinstance(val, str):
                return val.format(**values)
            else:
                raise PipelineError("template_fill() can only be used on strings.")
        new_pipeline_func = lambda x: _template_fill_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Dictionary Methods ---

    def with_items(self) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Convert a dictionary to an iterable of (key, value) pairs."""
        def _with_items_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, dict):
                yield from val.items()
            else:
                raise PipelineError("with_items() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _with_items_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def map_keys(self, func: Callable[[Any], Any]) -> 'Pipeline[dict[Any, Any]]':
        """Apply a function to all keys in a dictionary."""
        executable = self._unwrap(func)
        def _map_keys_func(val: Any) -> dict[Any, Any]:
            if isinstance(val, dict):
                return {executable(k): v for k, v in val.items()}
            else:
                raise PipelineError("map_keys() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _map_keys_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def map_values(self, func: Callable[[Any], Any]) -> 'Pipeline[dict[Any, Any]]':
        """Apply a function to all values in a dictionary."""
        executable = self._unwrap(func)
        def _map_values_func(val: Any) -> dict[Any, Any]:
            if isinstance(val, dict):
                return {k: executable(v) for k, v in val.items()}
            else:
                raise PipelineError("map_values() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _map_values_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Side Effect Methods ---

    def do(self, func: Callable[[Any], Any]) -> 'Pipeline[T]':
        """Apply a side-effect function without changing the value."""
        executable = self._unwrap(func)
        def _do_func(val: Any) -> Any:
            executable(val)
            return val
        new_pipeline_func = lambda x: _do_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def tap(self, func: Callable[[Any], Any]) -> 'Pipeline[T]':
        """Alias for do() - apply a side-effect function without changing the value."""
        return self.do(func)

    def debug(self, label: str = "DEBUG") -> 'Pipeline[T]':
        """Print the current value for debugging purposes."""
        def _debug_func(val: Any) -> Any:
            print(f"{label}: {val}")
            return val
        new_pipeline_func = lambda x: _debug_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def trace(self, label: str) -> 'Pipeline[T]':
        """Print the current value with a custom label for tracing."""
        return self.debug(label)

    def _unwrap(self, func: Any) -> Callable[[Any], Any]:
        """Unwraps a function or placeholder into an executable callable."""
        if isinstance(func, Placeholder):
            return func._func  # Access the single-argument callable from the placeholder
        elif callable(func):
            return func
        elif isinstance(func, dict):
            # Handle dictionary templates with placeholders
            return self._create_dict_mapper(func)
        elif isinstance(func, str) and '{' in func:
            # Handle f-string-like templates
            return self._create_string_formatter(func)
        else:
            raise PipelineError("Provided object is not callable or a valid placeholder.")
    
    def _create_dict_mapper(self, template: dict[str, Any]) -> Callable[[Any], dict[str, Any]]:
        """Create a function that maps an item to a dictionary using placeholder templates."""
        def dict_mapper(item: Any) -> dict[str, Any]:
            result = {}
            for key, value_template in template.items():
                if isinstance(value_template, Placeholder):
                    result[key] = value_template._func(item)
                elif callable(value_template):
                    result[key] = value_template(item)
                else:
                    result[key] = value_template
            return result
        return dict_mapper
    
    def _create_string_formatter(self, template: str) -> Callable[[Any], str]:
        """Create a function that formats a string template using item data."""
        def string_formatter(item: Any) -> str:
            # Handle f-string-like syntax by evaluating placeholders
            import re
            
            def replace_placeholder(match):
                expr = match.group(1)
                try:
                    # Create a safe evaluation context with the item
                    if isinstance(item, dict):
                        # For dict items, allow direct key access
                        context = {'_': item, **item}
                    else:
                        context = {'_': item}
                    
                    # Handle formatting specifiers
                    if ':' in expr:
                        expr_part, format_spec = expr.rsplit(':', 1)
                        result = eval(expr_part, {"__builtins__": {}}, context)
                        return f"{result:{format_spec}}"
                    else:
                        # Evaluate the expression
                        result = eval(expr, {"__builtins__": {}}, context)
                        return str(result)
                        
                except Exception as e:
                    # If evaluation fails, try simple key lookup for dict items
                    if isinstance(item, dict) and expr in item:
                        return str(item[expr])
                    return match.group(0)  # Return original if evaluation fails
            
            # Replace {expression} patterns
            formatted = re.sub(r'\{([^}]+)\}', replace_placeholder, template)
            return formatted
        
        return string_formatter

    def __call__(self, value: T) -> Any:
        """Make the pipeline callable with an input value."""
        # When called, the pipeline applies its accumulated function to the provided value
        return self._pipeline_func(value)

    def add(self, number: Any) -> 'Pipeline[Any]':
        """Add a number to the current value."""
        return self.apply(lambda x: (x or 0) + number)

    def subtract(self, number: Any) -> 'Pipeline[Any]':
        """Subtract a number from the current value."""
        return self.apply(lambda x: (x or 0) - number)

# Decorator for creating a pipeline from a function
def pipeline(func: Callable[['Pipeline[Any]'], 'Pipeline[Any]']) -> Callable[[Any], 'Pipeline[Any]']:
    """Decorator to create a pipeline from a function."""
    def wrapper(initial_value: Any) -> 'Pipeline[Any]':
        p: Pipeline[Any] = Pipeline(initial_value=initial_value)
        return func(p)
    return wrapper

def pipe(value: T) -> 'Pipeline[T]':
    """Creates a new Pipeline instance with the given initial value."""
    return Pipeline(initial_value=value)


# Only define Go backend methods if native_go is available
if native_go is not None:
    class GoBitwiseMethods:
        def bitwise_and_go(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise AND on each element in an iterable using Go backend."""
            def _bitwise_and_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.bitwise_and(list(val), operand)
                else:
                    raise PipelineError("bitwise_and_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _bitwise_and_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

        def bitwise_or_go(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise OR on each element in an iterable using Go backend."""
            def _bitwise_or_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.bitwise_or(list(val), operand)
                else:
                    raise PipelineError("bitwise_or_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _bitwise_or_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

        def bitwise_xor_go(self, operand: int) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise XOR on each element in an iterable using Go backend."""
            def _bitwise_xor_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.bitwise_xor(list(val), operand)
                else:
                    raise PipelineError("bitwise_xor_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _bitwise_xor_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

        def bitwise_not_go(self) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise NOT on each element in an iterable using Go backend."""
            def _bitwise_not_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.bitwise_not(list(val))
                else:
                    raise PipelineError("bitwise_not_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _bitwise_not_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

        def left_shift_go(self, bits: int) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise left shift on each element in an iterable using Go backend."""
            def _left_shift_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.left_shift(list(val), bits)
                else:
                    raise PipelineError("left_shift_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _left_shift_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

        def right_shift_go(self, bits: int) -> 'Pipeline[Generator[int, None, None]]':
            """Perform a bitwise right shift on each element in an iterable using Go backend."""
            def _right_shift_go_func(val: Any) -> Generator[int, None, None]:
                from . import native_go
                if native_go is None:
                    raise PipelineError("Go backend not available.")
                if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                    return native_go.right_shift_go(list(val), bits)
                else:
                    raise PipelineError("right_shift_go() can only be used on iterables of integers.")
            new_pipeline_func = lambda x: _right_shift_go_func(self._pipeline_func(x))
            return Pipeline(self._initial_value, new_pipeline_func)

    # Dynamically add GoBitwiseMethods to Pipeline if native_go is available
    for name in dir(GoBitwiseMethods):
        if not name.startswith('_'):
            setattr(Pipeline, name, getattr(GoBitwiseMethods, name))
