"""A simple Python library to calculate averages of values."""

from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

from deprecated import deprecated

from averager._utils import _optional_int

if TYPE_CHECKING:
    from collections.abc import Iterable

__version__ = importlib.metadata.version('averager')


@deprecated(
    version='3.1.0', reason='Use the built-in statistics module instead of Averager.'
)
def average(*values: float) -> float | int:
    """Calculate an unweighted average.

    Args:
        values: The values to find the average of

    Returns:
        The average of the inputs

    Example:
        >>> average(1, 2, 3)
        2
    """
    res = sum(values) / len(values)

    return _optional_int(res)


@deprecated(
    version='3.1.0', reason='Use the built-in statistics module instead of Averager.'
)
def weighted_average(*values: Iterable[float | int]) -> float | int:
    """Calculate a weighted average.

    Args:
        values: The values to find the average as an iterable of
            ``(value, weight)`` pairs

    Returns:
        The weighted average of the inputs

    Raises:
        ValueError: If any weight is less than zero

    Example:
        >>> weighted_average((1, 2), (2, 3))
        1.6
    """
    dividend, divisor = 0.0, 0.0

    for value, weight in values:
        if weight < 0:
            error = 'Weights cannot be less than zero'
            raise ValueError(error)

        dividend += value * weight
        divisor += weight

    res = dividend / divisor

    return _optional_int(res)


@deprecated(
    version='3.1.0', reason='Use the built-in statistics module instead of Averager.'
)
def median(*values: float) -> float | int:
    """Calculate the median, or middle number.

    Args:
        values: The values to find the median of

    Returns:
        The median of the inputs

    Examples:
        >>> median(1, 2, 3)
        2

        >>> median(1, 2, 3, 4)
        2.5
    """
    sorted_values = sorted(values)
    middle = len(values) // 2

    if len(values) % 2 == 0:
        return average(sorted_values[middle], sorted_values[middle - 1])

    return _optional_int(sorted_values[middle])


@deprecated(
    version='3.1.0', reason='Use the built-in statistics module instead of Averager.'
)
def mode(*values: float) -> float | int | set[float | int]:
    """Calculate the mode, or most common value.

    Args:
        values: The values to find the mode of

    Returns:
        The mode(s) of the inputs (returned as a set if more than one)

    Examples:
        >>> mode(1, 2, 2, 3)
        2

        >>> mode(1, 1, 2, 2)
        {1, 2}
    """
    counts: dict[float | int, int] = {}

    for value in values:
        counts[value] = counts.get(value, 0) + 1

    result = {k for k, v in counts.items() if v == max(counts.values())}

    if len(result) == 1:
        return result.pop()

    return result
