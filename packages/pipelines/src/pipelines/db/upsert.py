"""Idempotent upsert helpers for pipeline data writes.

All writes are ON CONFLICT DO UPDATE — safe to re-run the same pipeline
for the same date without producing duplicates.
"""
import uuid
from datetime import date
from typing import Sequence

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.interfaces.market_data import OHLCVBar
from shared.utils.idempotency import ohlcv_idempotency_key

logger = structlog.get_logger()


async def upsert_ticker(
    session: AsyncSession,
    symbol: str,
    market: str,
    asset_type: str,
    name: str | None = None,
    currency: str = "USD",
    exchange: str | None = None,
) -> uuid.UUID:
    """Upsert a ticker row; return its UUID."""
    result = await session.execute(
        text("""
            INSERT INTO raw.tickers (symbol, market, asset_type, name, currency, exchange)
            VALUES (:symbol, :market, :asset_type, :name, :currency, :exchange)
            ON CONFLICT (symbol) DO UPDATE
                SET market      = EXCLUDED.market,
                    asset_type  = EXCLUDED.asset_type,
                    name        = COALESCE(EXCLUDED.name, raw.tickers.name),
                    currency    = EXCLUDED.currency,
                    exchange    = COALESCE(EXCLUDED.exchange, raw.tickers.exchange),
                    updated_at  = now()
            RETURNING id
        """),
        {
            "symbol": symbol,
            "market": market,
            "asset_type": asset_type,
            "name": name,
            "currency": currency,
            "exchange": exchange,
        },
    )
    row = result.fetchone()
    return row[0]  # type: ignore[index]


async def upsert_ohlcv_bars(
    session: AsyncSession,
    bars: Sequence[OHLCVBar],
    ticker_id_map: dict[str, uuid.UUID],
) -> int:
    """Bulk-upsert OHLCV bars. Returns count of rows inserted/updated.

    Uses deterministic UUID keys so re-runs produce no duplicates.
    ticker_id_map: {symbol -> ticker UUID from raw.tickers}
    """
    if not bars:
        return 0

    rows = []
    for bar in bars:
        ticker_id = ticker_id_map.get(bar.ticker)
        if ticker_id is None:
            logger.warning("ohlcv_upsert_missing_ticker", symbol=bar.ticker)
            continue
        rows.append({
            "id": ohlcv_idempotency_key(bar.ticker, bar.date),
            "ticker_id": ticker_id,
            "symbol": bar.ticker,
            "date": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "adjusted_close": bar.adjusted_close,
        })

    if not rows:
        return 0

    await session.execute(
        text("""
            INSERT INTO raw.ohlcv_daily
                (id, ticker_id, symbol, date, open, high, low, close, volume, adjusted_close)
            VALUES
                (:id, :ticker_id, :symbol, :date, :open, :high, :low, :close, :volume, :adjusted_close)
            ON CONFLICT (symbol, date) DO UPDATE
                SET open          = EXCLUDED.open,
                    high          = EXCLUDED.high,
                    low           = EXCLUDED.low,
                    close         = EXCLUDED.close,
                    volume        = EXCLUDED.volume,
                    adjusted_close = COALESCE(EXCLUDED.adjusted_close, raw.ohlcv_daily.adjusted_close),
                    fetched_at    = now()
        """),
        rows,
    )
    logger.info("ohlcv_upsert_complete", count=len(rows))
    return len(rows)


async def insert_pipeline_run_start(
    session: AsyncSession,
    pipeline_name: str,
    run_date: date,
    market: str,
    correlation_id: uuid.UUID,
    triggered_by: str = "scheduler",
) -> uuid.UUID:
    """Insert a pipeline_runs row with status='running'. Returns the run ID."""
    run_id = uuid.uuid4()
    await session.execute(
        text("""
            INSERT INTO meta.pipeline_runs
                (id, pipeline_name, run_date, market, status, correlation_id, triggered_by)
            VALUES
                (:id, :pipeline_name, :run_date, :market, 'running', :correlation_id, :triggered_by)
        """),
        {
            "id": run_id,
            "pipeline_name": pipeline_name,
            "run_date": run_date,
            "market": market,
            "correlation_id": correlation_id,
            "triggered_by": triggered_by,
        },
    )
    await session.commit()
    return run_id


async def finalize_pipeline_run(
    session: AsyncSession,
    run_id: uuid.UUID,
    status: str,
    rows_processed: int,
    tickers_attempted: int,
    tickers_succeeded: int,
    error_message: str | None = None,
) -> None:
    """Update a pipeline_runs row to terminal status."""
    await session.execute(
        text("""
            UPDATE meta.pipeline_runs
            SET status             = :status,
                finished_at        = now(),
                rows_processed     = :rows_processed,
                tickers_attempted  = :tickers_attempted,
                tickers_succeeded  = :tickers_succeeded,
                error_message      = :error_message
            WHERE id = :run_id
        """),
        {
            "run_id": run_id,
            "status": status,
            "rows_processed": rows_processed,
            "tickers_attempted": tickers_attempted,
            "tickers_succeeded": tickers_succeeded,
            "error_message": error_message,
        },
    )
    await session.commit()
