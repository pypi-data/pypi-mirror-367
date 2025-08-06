"""
Pure Python implementations of bitwise operations.
"""

from collections.abc import Iterable, Generator
from typing import Union

def bitwise_and(data: Iterable[int], operand: int) -> Generator[int, None, None]:
    """Performs a bitwise AND operation on each element."""
    for item in data:
        yield item & operand

def bitwise_or(data: Iterable[int], operand: int) -> Generator[int, None, None]:
    """Performs a bitwise OR operation on each element."""
    for item in data:
        yield item | operand

def bitwise_xor(data: Iterable[int], operand: int) -> Generator[int, None, None]:
    """Performs a bitwise XOR operation on each element."""
    for item in data:
        yield item ^ operand

def bitwise_not(data: Iterable[int]) -> Generator[int, None, None]:
    """Performs a bitwise NOT operation on each element."""
    for item in data:
        yield ~item

def left_shift(data: Iterable[int], bits: int) -> Generator[int, None, None]:
    """Performs a bitwise left shift on each element."""
    for item in data:
        yield item << bits

def right_shift(data: Iterable[int], bits: int) -> Generator[int, None, None]:
    """Performs a bitwise right shift on each element."""
    for item in data:
        yield item >> bits
