from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import pandas as pd


class StrategySignal(StrEnum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NEUTRAL = "neutral"


@dataclass
class ScreenerResult:
    ticker: str
    signal: StrategySignal
    score: float  # 0.0–1.0 confidence / strength
    metadata: dict[str, Any]  # strategy-specific details (e.g., rsi_value, crossover_date)


class BaseStrategy(ABC):
    """Plugin interface for screener strategies. Public strategies shipped in /packages/pipelines.
    Private strategies loaded at runtime via PLUGIN_STRATEGY_PATH env var."""

    name: str  # unique strategy identifier, used as table prefix
    description: str

    @abstractmethod
    def evaluate(self, df: pd.DataFrame, ticker: str) -> ScreenerResult:
        """Given a DataFrame of OHLCV bars (sorted ascending by date), return a signal.

        DataFrame columns: open, high, low, close, volume, adjusted_close
        DataFrame index: DatetimeIndex
        """
        ...
