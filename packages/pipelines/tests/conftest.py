"""Synthetic OHLCV fixtures for strategy and provider tests."""
import random
from datetime import date, timedelta

import pandas as pd
import pytest


def make_ohlcv_df(
    start: date = date(2024, 1, 2),
    periods: int = 60,
    seed: int = 42,
    trend: float = 0.001,
) -> pd.DataFrame:
    """Generate a synthetic OHLCV DataFrame with controlled randomness."""
    rng = random.Random(seed)
    dates = [start + timedelta(days=i) for i in range(periods)]
    close = 1000.0
    rows = []
    for d in dates:
        close *= 1 + trend + rng.uniform(-0.02, 0.02)
        high = close * (1 + rng.uniform(0.001, 0.015))
        low = close * (1 - rng.uniform(0.001, 0.015))
        open_ = close * (1 + rng.uniform(-0.005, 0.005))
        volume = int(rng.uniform(1_000_000, 50_000_000))
        rows.append({
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Adj Close": close * 0.98,
            "Volume": volume,
        })
    df = pd.DataFrame(rows, index=pd.DatetimeIndex(dates))
    return df


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    return make_ohlcv_df()


@pytest.fixture
def bullish_ohlcv_df() -> pd.DataFrame:
    """Strong uptrend — should produce BUY signals for trend strategies."""
    return make_ohlcv_df(trend=0.008, seed=1)


@pytest.fixture
def bearish_ohlcv_df() -> pd.DataFrame:
    """Downtrend — should produce SELL signals for trend strategies."""
    return make_ohlcv_df(trend=-0.008, seed=2)
