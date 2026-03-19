"""climate analysis functions."""

from __future__ import annotations

import numpy as np
from scipy import stats


def compute_mean(data: list[float] | np.ndarray) -> float:
    """Return the temporal mean of a climate time series.

    Args:
        data: Sequence of numeric climate values (e.g. temperatures).

    Returns:
        Arithmetic mean of the series.

    Raises:
        ValueError: If *data* is empty.
    """
    arr = np.asarray(data, dtype=float)
    if arr.size == 0:
        raise ValueError("data must not be empty.")
    return float(np.mean(arr))


def compute_anomaly(
    data: list[float] | np.ndarray,
    baseline: list[float] | np.ndarray,
) -> np.ndarray:
    """Compute anomalies relative to a baseline period.

    Each value in *data* has the mean of *baseline* subtracted from it,
    yielding the departure from the reference climatology.

    Args:
        data: Observed climate series.
        baseline: Reference period used to derive the climatological mean.

    Returns:
        Array of anomaly values with the same length as *data*.

    Raises:
        ValueError: If either array is empty.
    """
    arr = np.asarray(data, dtype=float)
    base = np.asarray(baseline, dtype=float)

    if arr.size == 0 or base.size == 0:
        raise ValueError("data and baseline must not be empty.")

    return arr - float(np.mean(base))


def detect_trend(data: list[float] | np.ndarray) -> dict[str, float]:
    """Detect a linear trend in a climate time series via OLS regression.

    Args:
        data: Sequence of numeric climate values ordered in time.

    Returns:
        Dictionary with keys:
            - ``slope``      : change per time step (same units as *data*)
            - ``intercept``  : fitted value at t=0
            - ``r_squared``  : coefficient of determination (0–1)
            - ``p_value``    : two-sided p-value for the slope

    Raises:
        ValueError: If *data* has fewer than two points.
    """
    arr = np.asarray(data, dtype=float)
    if arr.size < 2:
        raise ValueError("detect_trend requires at least two data points.")

    time = np.arange(len(arr), dtype=float)
    slope, intercept, r_value, p_value, _ = stats.linregress(time, arr)

    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value**2),
        "p_value": float(p_value),
    }
