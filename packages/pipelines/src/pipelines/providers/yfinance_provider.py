"""yfinance implementation of MarketDataProvider.

Known limitations (documented, not hidden):
- IDX tickers require ".JK" suffix (e.g., "BBCA.JK")
- yfinance rate-limits at ~2000 requests/hour; batch calls reduce per-request count
- Some IDX tickers have spotty coverage; gaps are logged, not treated as errors
- Adjusted close may be None for some markets
"""
import asyncio
from datetime import date
from typing import Sequence

import structlog
import yfinance as yf

from shared.interfaces.market_data import MarketDataProvider, OHLCVBar
from shared.utils.retry import with_retry

logger = structlog.get_logger()

# yfinance batch size — above ~50 tickers per call can trigger rate limits
_BATCH_SIZE = 20


class YFinanceProvider(MarketDataProvider):
    """Wraps yfinance.download with retry, batching, and structured logging."""

    async def fetch_ohlcv(
        self,
        tickers: Sequence[str],
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        all_bars: list[OHLCVBar] = []
        ticker_list = list(tickers)

        for batch_start in range(0, len(ticker_list), _BATCH_SIZE):
            batch = ticker_list[batch_start : batch_start + _BATCH_SIZE]
            bars = await asyncio.get_event_loop().run_in_executor(
                None,
                self._fetch_batch,
                batch,
                start_date,
                end_date,
            )
            all_bars.extend(bars)
            # Polite delay between batches to respect yfinance rate limits
            if batch_start + _BATCH_SIZE < len(ticker_list):
                await asyncio.sleep(1.0)

        return all_bars

    @with_retry(max_attempts=3, min_wait=2.0, max_wait=30.0, exceptions=(Exception,))
    def _fetch_batch(
        self,
        tickers: list[str],
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        logger.info(
            "yfinance_fetch_batch",
            tickers=tickers,
            start=str(start_date),
            end=str(end_date),
        )

        df = yf.download(
            tickers=" ".join(tickers),
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            auto_adjust=False,
            progress=False,
            group_by="ticker" if len(tickers) > 1 else "column",
            threads=True,
        )

        if df.empty:
            logger.warning("yfinance_empty_response", tickers=tickers)
            return []

        bars: list[OHLCVBar] = []

        if len(tickers) == 1:
            # Single ticker: columns are Open, High, Low, Close, Adj Close, Volume
            bars.extend(self._parse_single_ticker_df(df, tickers[0]))
        else:
            # Multiple tickers: MultiIndex columns (ticker, field)
            for ticker in tickers:
                if ticker not in df.columns.get_level_values(0):
                    logger.warning("yfinance_ticker_missing", ticker=ticker)
                    continue
                ticker_df = df[ticker]
                bars.extend(self._parse_single_ticker_df(ticker_df, ticker))

        return bars

    def _parse_single_ticker_df(self, df: object, ticker: str) -> list[OHLCVBar]:
        import pandas as pd

        if not isinstance(df, pd.DataFrame):
            return []

        result: list[OHLCVBar] = []
        for idx, row in df.iterrows():
            # Skip rows where close is NaN (market holiday gaps in yfinance data)
            close_val = row.get("Close")
            if close_val is None or (hasattr(close_val, "__float__") and __import__("math").isnan(float(close_val))):
                continue

            trading_date = idx.date() if hasattr(idx, "date") else idx

            adj_close = row.get("Adj Close")
            adj_close_val = None
            if adj_close is not None:
                try:
                    adj_close_float = float(adj_close)
                    import math
                    if not math.isnan(adj_close_float):
                        adj_close_val = adj_close_float
                except (TypeError, ValueError):
                    pass

            result.append(
                OHLCVBar(
                    ticker=ticker,
                    date=trading_date,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(close_val),
                    volume=int(row.get("Volume", 0) or 0),
                    adjusted_close=adj_close_val,
                )
            )

        return result

    async def validate_ticker(self, ticker: str) -> bool:
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: yf.Ticker(ticker).fast_info
            )
            return bool(getattr(info, "last_price", None))
        except Exception:
            return False
