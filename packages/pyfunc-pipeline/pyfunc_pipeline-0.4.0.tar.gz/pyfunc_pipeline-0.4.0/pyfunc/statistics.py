"""
Pure Python implementations of statistical operations.
"""

import math
from collections.abc import Iterable
from typing import List, Union

def median(data: Iterable[Union[int, float]]) -> Union[int, float]:
    """Calculates the median of a sequence of numbers."""
    sorted_data: List[Union[int, float]] = sorted(data)
    n = len(sorted_data)
    if n == 0:
        raise ValueError("median() arg is an empty sequence")
    
    mid_index = n // 2
    
    if n % 2 == 1:
        # Odd number of elements
        return sorted_data[mid_index]
    else:
        # Even number of elements
        return (sorted_data[mid_index - 1] + sorted_data[mid_index]) / 2

def stdev(data: Iterable[Union[int, float]]) -> float:
    """
    Calculates the population standard deviation of a sequence of numbers.
    """
    data_list: List[Union[int, float]] = list(data)
    n = len(data_list)
    
    if n < 2:
        raise ValueError("stdev() requires at least two data points")
    
    mean = sum(data_list) / n
    variance = sum((x - mean) ** 2 for x in data_list) / n
    
    return math.sqrt(variance)
