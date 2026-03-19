"""Fetch historical climate data from the Open-Meteo Archive API."""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx
import numpy as np

_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Variables available in the Open-Meteo daily archive
DAILY_VARIABLES = frozenset(
    [
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "windspeed_10m_max",
        "et0_fao_evapotranspiration",
        "shortwave_radiation_sum",
    ]
)


def fetch_historical(
    latitude: float,
    longitude: float,
    start: str | date,
    end: str | date,
    variable: str = "temperature_2m_mean",
    *,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch daily climate data from the Open-Meteo Archive API.

    Args:
        latitude:  Decimal latitude of the location (e.g. ``48.8566``).
        longitude: Decimal longitude of the location (e.g. ``2.3522``).
        start:     Start date as ``"YYYY-MM-DD"`` string or :class:`datetime.date`.
        end:       End date as ``"YYYY-MM-DD"`` string or :class:`datetime.date`.
        variable:  Daily variable to retrieve.  Must be one of
                   :data:`DAILY_VARIABLES`.  Defaults to
                   ``"temperature_2m_mean"``.
        timeout:   HTTP request timeout in seconds.

    Returns:
        Dictionary with keys:

        - ``"dates"``    : list of ISO date strings (``"YYYY-MM-DD"``)
        - ``"values"``   : :class:`numpy.ndarray` of float64 values
        - ``"variable"`` : the requested variable name
        - ``"latitude"`` : echoed latitude
        - ``"longitude"``: echoed longitude
        - ``"unit"``     : unit string as reported by the API

    Raises:
        ValueError:  If *variable* is not supported or dates are invalid.
        RuntimeError: If the API returns an error response.
        ImportError: If ``httpx`` is not installed.
    """
    if variable not in DAILY_VARIABLES:
        raise ValueError(
            f"Unsupported variable '{variable}'. "
            f"Choose from: {sorted(DAILY_VARIABLES)}"
        )

    start_str = start.isoformat() if isinstance(start, date) else start
    end_str = end.isoformat() if isinstance(end, date) else end

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_str,
        "end_date": end_str,
        "daily": variable,
        "timezone": "UTC",
    }

    response = httpx.get(_ARCHIVE_URL, params=params, timeout=timeout)

    if response.status_code != 200:
        raise RuntimeError(
            f"Open-Meteo API error {response.status_code}: {response.text}"
        )

    payload = response.json()

    if "error" in payload:
        raise RuntimeError(f"Open-Meteo API returned an error: {payload['error']}")

    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    raw_values = daily.get(variable, [])

    values = np.array(
        [float(v) if v is not None else float("nan") for v in raw_values],
        dtype=float,
    )

    units = payload.get("daily_units", {}).get(variable, "")

    return {
        "dates": dates,
        "values": values,
        "variable": variable,
        "latitude": latitude,
        "longitude": longitude,
        "unit": units,
    }
