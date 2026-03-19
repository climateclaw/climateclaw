"""Unit tests for climateclaw.analysis."""

import math
import pytest
import numpy as np

from climateclaw.analysis import compute_mean, compute_anomaly, detect_trend


class TestComputeMean:
    def test_basic(self):
        assert compute_mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)

    def test_single_value(self):
        assert compute_mean([42.0]) == pytest.approx(42.0)

    def test_numpy_input(self):
        arr = np.array([10.0, 20.0, 30.0])
        assert compute_mean(arr) == pytest.approx(20.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            compute_mean([])


class TestComputeAnomaly:
    def test_basic(self):
        # baseline mean = 10, so anomalies = data - 10
        result = compute_anomaly([11.0, 12.0, 9.0], baseline=[8.0, 10.0, 12.0])
        expected = np.array([1.0, 2.0, -1.0])
        np.testing.assert_allclose(result, expected)

    def test_zero_anomaly_when_equal_to_baseline_mean(self):
        baseline = [5.0, 15.0]  # mean = 10
        data = [10.0]
        np.testing.assert_allclose(compute_anomaly(data, baseline), [0.0])

    def test_empty_data_raises(self):
        with pytest.raises(ValueError):
            compute_anomaly([], [1.0, 2.0])

    def test_empty_baseline_raises(self):
        with pytest.raises(ValueError):
            compute_anomaly([1.0], [])


class TestDetectTrend:
    def test_perfect_positive_trend(self):
        data = [0.0, 1.0, 2.0, 3.0, 4.0]
        result = detect_trend(data)
        assert result["slope"] == pytest.approx(1.0)
        assert result["r_squared"] == pytest.approx(1.0)
        assert result["p_value"] == pytest.approx(0.0, abs=1e-10)

    def test_perfect_negative_trend(self):
        data = [4.0, 3.0, 2.0, 1.0, 0.0]
        result = detect_trend(data)
        assert result["slope"] == pytest.approx(-1.0)
        assert result["r_squared"] == pytest.approx(1.0)

    def test_flat_series(self):
        data = [5.0] * 10
        result = detect_trend(data)
        assert result["slope"] == pytest.approx(0.0, abs=1e-10)

    def test_returns_expected_keys(self):
        result = detect_trend([1.0, 2.0, 3.0])
        assert set(result.keys()) == {"slope", "intercept", "r_squared", "p_value"}

    def test_single_point_raises(self):
        with pytest.raises(ValueError, match="two"):
            detect_trend([1.0])

    def test_all_values_finite(self):
        result = detect_trend([1.0, 2.0, 3.0])
        assert all(math.isfinite(v) for v in result.values())
