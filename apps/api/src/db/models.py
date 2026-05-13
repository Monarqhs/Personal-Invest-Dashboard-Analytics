"""SQLAlchemy ORM models — single source of truth for Alembic migrations."""
import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Explicit naming convention so Alembic can auto-generate constraint names
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


# ─── meta schema ─────────────────────────────────────────────────────────────

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    __table_args__ = {"schema": "meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_name: Mapped[str] = mapped_column(String(100), nullable=False)
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)  # 'IDX' | 'US'
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # 'running'|'success'|'partial'|'failed'
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rows_processed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tickers_attempted: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tickers_succeeded: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduler")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


# ─── raw schema ──────────────────────────────────────────────────────────────

class Ticker(Base):
    __tablename__ = "tickers"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    market: Mapped[str] = mapped_column(String(10), nullable=False)   # 'IDX' | 'US'
    asset_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'stock' | 'etf' | 'index'
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    exchange: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class OHLCVDaily(Base):
    __tablename__ = "ohlcv_daily"
    __table_args__ = (
        Index("ix_raw_ohlcv_daily_symbol_date", "symbol", "date"),
        {"schema": "raw"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw.tickers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  # denormalized
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    adjusted_close: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ─── meta schema — watchlist ─────────────────────────────────────────────────

class WatchlistItem(Base):
    __tablename__ = "watchlist"
    __table_args__ = (
        Index("ix_meta_watchlist_user_symbol", "user_id", "symbol", unique=True),
        {"schema": "meta"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, default=SYSTEM_USER_ID
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


# ─── screener schema ─────────────────────────────────────────────────────────

class ScreenerResultBase(Base):
    """Abstract base — subclassed per timeframe."""
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    signal: Mapped[str] = mapped_column(String(20), nullable=False)  # StrategySignal
    score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class ScreenerResultDaily(ScreenerResultBase):
    __tablename__ = "results_daily"
    __table_args__ = (
        Index("ix_screener_daily_symbol_date", "symbol", "as_of_date"),
        Index("ix_screener_daily_strategy_date", "strategy_name", "as_of_date"),
        {"schema": "screener"},
    )


class ScreenerResultWeekly(ScreenerResultBase):
    __tablename__ = "results_weekly"
    __table_args__ = (
        Index("ix_screener_weekly_symbol_date", "symbol", "as_of_date"),
        {"schema": "screener"},
    )


class ScreenerResultMonthly(ScreenerResultBase):
    __tablename__ = "results_monthly"
    __table_args__ = (
        Index("ix_screener_monthly_symbol_date", "symbol", "as_of_date"),
        {"schema": "screener"},
    )
