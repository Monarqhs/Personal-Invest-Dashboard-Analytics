from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Sequence

from pydantic import BaseModel, Field


class OHLCVBar(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: float | None = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class MarketDataProvider(ABC):
    """Abstraction over market data sources. Swap yfinance for premium provider without touching callers."""

    @abstractmethod
    async def fetch_ohlcv(
        self,
        tickers: Sequence[str],
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        """Fetch OHLCV bars for a batch of tickers. Must be idempotent."""
        ...

    @abstractmethod
    async def validate_ticker(self, ticker: str) -> bool:
        """Return True if the ticker is known and tradeable."""
        ...
