"""Unit tests for YFinanceProvider — yfinance.download is mocked throughout."""
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pipelines.providers.yfinance_provider import YFinanceProvider  # noqa: E402


def _make_single_ticker_df(ticker: str, n: int = 5) -> pd.DataFrame:
    """Minimal DataFrame matching yfinance.download single-ticker output."""
    dates = pd.date_range("2024-01-02", periods=n, freq="B")
    return pd.DataFrame(
        {
            "Open":      [100.0 + i for i in range(n)],
            "High":      [102.0 + i for i in range(n)],
            "Low":       [98.0  + i for i in range(n)],
            "Close":     [101.0 + i for i in range(n)],
            "Adj Close": [100.5 + i for i in range(n)],
            "Volume":    [1_000_000] * n,
        },
        index=dates,
    )


@pytest.mark.asyncio
async def test_fetch_single_ticker_returns_correct_bars() -> None:
    provider = YFinanceProvider()
    mock_df = _make_single_ticker_df("AAPL", n=3)

    with patch("yfinance.download", return_value=mock_df):
        bars = await provider.fetch_ohlcv(
            tickers=["AAPL"],
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
        )

    assert len(bars) == 3
    assert all(b.ticker == "AAPL" for b in bars)
    assert bars[0].close == 101.0
    assert bars[0].volume == 1_000_000
    assert bars[0].adjusted_close == 100.5


@pytest.mark.asyncio
async def test_fetch_empty_df_returns_empty_list() -> None:
    provider = YFinanceProvider()

    with patch("yfinance.download", return_value=pd.DataFrame()):
        bars = await provider.fetch_ohlcv(
            tickers=["INVALID"],
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
        )

    assert bars == []


@pytest.mark.asyncio
async def test_fetch_skips_nan_close_rows() -> None:
    provider = YFinanceProvider()
    import math
    df = _make_single_ticker_df("SPY", n=3)
    df.at[df.index[1], "Close"] = float("nan")  # middle row is NaN

    with patch("yfinance.download", return_value=df):
        bars = await provider.fetch_ohlcv(
            tickers=["SPY"],
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
        )

    assert len(bars) == 2
    assert not any(math.isnan(b.close) for b in bars)


@pytest.mark.asyncio
async def test_fetch_batches_large_ticker_list() -> None:
    """Verifies that >20 tickers trigger multiple yfinance.download calls."""
    provider = YFinanceProvider()
    tickers = [f"T{i:02d}" for i in range(25)]

    call_count = 0

    def mock_download(*args: object, **kwargs: object) -> pd.DataFrame:
        nonlocal call_count
        call_count += 1
        return pd.DataFrame()  # empty — just counting calls

    with patch("yfinance.download", side_effect=mock_download):
        with patch("asyncio.sleep"):  # don't actually sleep in tests
            await provider.fetch_ohlcv(
                tickers=tickers,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
            )

    # 25 tickers / batch_size 20 = 2 batches
    assert call_count == 2
