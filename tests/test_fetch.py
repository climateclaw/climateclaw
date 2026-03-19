"""Unit tests for climateclaw.fetch"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from climateclaw.fetch import DAILY_VARIABLES, fetch_historical

_MOCK_RESPONSE = {
    "daily": {
        "time": ["2020-01-01", "2020-01-02", "2020-01-03"],
        "temperature_2m_mean": [3.1, 4.5, None],  # None simulates missing day
    },
    "daily_units": {"temperature_2m_mean": "°C"},
    "latitude": 48.8566,
    "longitude": 2.3522,
}


def _make_mock_response(payload: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.text = str(payload)
    return mock


class TestFetchHistorical:
    @patch("httpx.get")
    def test_returns_expected_keys(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        assert set(result.keys()) == {
            "dates",
            "values",
            "variable",
            "latitude",
            "longitude",
            "unit",
        }

    @patch("httpx.get")
    def test_values_are_numpy_array(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        assert isinstance(result["values"], np.ndarray)

    @patch("httpx.get")
    def test_none_values_become_nan(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        assert np.isnan(result["values"][2])

    @patch("httpx.get")
    def test_non_nan_values_are_correct(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        np.testing.assert_allclose(result["values"][:2], [3.1, 4.5])

    @patch("httpx.get")
    def test_unit_is_returned(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        assert result["unit"] == "°C"

    @patch("httpx.get")
    def test_date_object_accepted(self, mock_get):
        from datetime import date

        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        result = fetch_historical(
            48.8566,
            2.3522,
            date(2020, 1, 1),
            date(2020, 1, 3),
        )
        assert result["dates"] == ["2020-01-01", "2020-01-02", "2020-01-03"]

    @patch("httpx.get")
    def test_api_error_status_raises(self, mock_get):
        mock_get.return_value = _make_mock_response({}, status_code=400)
        with pytest.raises(RuntimeError, match="400"):
            fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")

    @patch("httpx.get")
    def test_api_error_field_raises(self, mock_get):
        mock_get.return_value = _make_mock_response({"error": "Invalid location"})
        with pytest.raises(RuntimeError, match="Invalid location"):
            fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")

    def test_unsupported_variable_raises(self):
        with pytest.raises(ValueError, match="Unsupported variable"):
            fetch_historical(
                48.8566,
                2.3522,
                "2020-01-01",
                "2020-01-03",
                variable="not_a_real_variable",
            )

    @patch("httpx.get")
    def test_output_feeds_into_compute_mean(self, mock_get):
        mock_get.return_value = _make_mock_response(_MOCK_RESPONSE)
        from climateclaw import compute_mean

        result = fetch_historical(48.8566, 2.3522, "2020-01-01", "2020-01-03")
        # drop NaNs before passing to compute_mean
        clean = result["values"][~np.isnan(result["values"])]
        assert compute_mean(clean) == pytest.approx(3.8)


class TestDailyVariables:
    def test_contains_temperature(self):
        assert "temperature_2m_mean" in DAILY_VARIABLES

    def test_contains_precipitation(self):
        assert "precipitation_sum" in DAILY_VARIABLES

    def test_is_frozenset(self):
        assert isinstance(DAILY_VARIABLES, frozenset)
