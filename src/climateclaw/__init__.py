"""climateclaw — Climate data analysis & statistics."""

from ._version import __version__  # noqa: F401
from .analysis import compute_anomaly, compute_mean, detect_trend
from .fetch import fetch_historical

__all__ = ["compute_mean", "compute_anomaly", "detect_trend", "fetch_historical"]
