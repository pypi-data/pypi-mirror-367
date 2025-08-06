from .pipeline import Pipeline, pipeline, pipe
from .placeholder import Placeholder
from .utils import square, increment, half
from .errors import PipelineError
try:
    from . import native_go
except ImportError:
    pass # Go backend not available
# Backend functionality
from .backends import (
    enable_cpp_backend, disable_cpp_backend, use_cpp_backend, is_cpp_available, 
    set_rust_threshold, set_zig_threshold, is_zig_available,
    set_go_threshold, is_go_available
)

_ = Placeholder()

# Make pipe the primary entry point
__all__ = [
    'pipe', 'Pipeline', 'pipeline', 'Placeholder', '_', 
    'square', 'increment', 'half', 'PipelineError',
    'enable_cpp_backend', 'disable_cpp_backend', 'use_cpp_backend', 'is_cpp_available',
    'set_rust_threshold', 'set_zig_threshold', 'is_zig_available',
    'set_go_threshold', 'is_go_available'
]
