from __future__ import annotations


def _optional_int(value: float) -> float | int:
    """Convert a ``float`` to an ``int`` if they're the same value.

    Args:
        value: The value to convert

    Returns:
        Either the original input or the input as an ``int``

    Example:
        >>> _optional_int(3.0)
        3

        >>> _optional_int(1.2)
        1.2
    """
    if value == int(value):
        return int(value)

    return value
