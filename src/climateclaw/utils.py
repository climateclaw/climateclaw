"""Utility helpers for unit conversion and data validation."""

from __future__ import annotations

import numpy as np


def celsius_to_fahrenheit(value: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return value * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(value: float) -> float:
    """Convert a temperature from Fahrenheit to Celsius."""
    return (value - 32.0) * 5.0 / 9.0


def kelvin_to_celsius(value: float) -> float:
    """Convert a temperature from Kelvin to Celsius."""
    return value - 273.15


def validate_series(data: list | np.ndarray, name: str = "data") -> np.ndarray:
    """Validate and coerce *data* to a 1-D float NumPy array.

    Args:
        data: Input sequence.
        name: Variable name used in error messages.

    Returns:
        1-D ``np.ndarray`` of dtype ``float64``.

    Raises:
        TypeError:  If *data* is not array-like.
        ValueError: If *data* is empty or contains non-finite values.
    """
    try:
        arr = np.asarray(data, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'{name}' must be array-like of numbers.") from exc

    if arr.ndim != 1:
        raise ValueError(f"'{name}' must be a 1-D sequence, got shape {arr.shape}.")
    if arr.size == 0:
        raise ValueError(f"'{name}' must not be empty.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"'{name}' contains NaN or infinite values.")

    return arr
