import pandas as pd
import pytest

from pls_regration.features import assert_features_available_at_origin


def test_allows_features_known_at_forecast_origin() -> None:
    frame = pd.DataFrame(
        {
            "forecast_origin": ["2026-01-02T00:00:00Z"],
            "available_at": ["2026-01-02T00:00:00Z"],
        }
    )
    assert_features_available_at_origin(frame)


def test_rejects_future_observed_information() -> None:
    frame = pd.DataFrame(
        {
            "forecast_origin": ["2026-01-02T00:00:00Z"],
            "available_at": ["2026-01-03T00:00:00Z"],
        }
    )
    with pytest.raises(ValueError, match="future information"):
        assert_features_available_at_origin(frame)
