"""Initial schemas: raw, meta, screener

Revision ID: 001
Revises:
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # ── Create schemas ────────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    op.execute("CREATE SCHEMA IF NOT EXISTS staging")
    op.execute("CREATE SCHEMA IF NOT EXISTS marts")
    op.execute("CREATE SCHEMA IF NOT EXISTS screener")
    op.execute("CREATE SCHEMA IF NOT EXISTS meta")

    # ── Seed system user (Supabase Auth manages the auth.users table;
    #    we only reference user_id as a UUID without a FK to auth.users
    #    so the app stays portable outside Supabase) ─────────────────────────

    # ── meta.pipeline_runs ────────────────────────────────────────────────────
    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pipeline_name", sa.String(100), nullable=False),
        sa.Column("run_date", sa.Date, nullable=False),
        sa.Column("market", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_processed", sa.Integer, nullable=True),
        sa.Column("tickers_attempted", sa.Integer, nullable=True),
        sa.Column("tickers_succeeded", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("triggered_by", sa.String(50), nullable=False, server_default="scheduler"),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        schema="meta",
    )
    op.create_index("ix_meta_pipeline_runs_run_date", "pipeline_runs", ["run_date"], schema="meta")
    op.create_index("ix_meta_pipeline_runs_status", "pipeline_runs", ["status"], schema="meta")

    # ── meta.watchlist ────────────────────────────────────────────────────────
    op.create_table(
        "watchlist",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text(f"'{SYSTEM_USER_ID}'::uuid")),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("notes", sa.Text, nullable=True),
        schema="meta",
    )
    op.create_index("ix_meta_watchlist_user_symbol", "watchlist", ["user_id", "symbol"], unique=True, schema="meta")

    # ── raw.tickers ───────────────────────────────────────────────────────────
    op.create_table(
        "tickers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("name", sa.Text, nullable=True),
        sa.Column("market", sa.String(10), nullable=False),
        sa.Column("asset_type", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="USD"),
        sa.Column("exchange", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="raw",
    )
    op.create_index("uq_raw_tickers_symbol", "tickers", ["symbol"], unique=True, schema="raw")

    # ── raw.ohlcv_daily ───────────────────────────────────────────────────────
    op.create_table(
        "ohlcv_daily",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("ticker_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("raw.tickers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("open", sa.Numeric(18, 6), nullable=False),
        sa.Column("high", sa.Numeric(18, 6), nullable=False),
        sa.Column("low", sa.Numeric(18, 6), nullable=False),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger, nullable=False),
        sa.Column("adjusted_close", sa.Numeric(18, 6), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        schema="raw",
    )
    op.create_index("ix_raw_ohlcv_daily_symbol_date", "ohlcv_daily", ["symbol", "date"], schema="raw")
    op.create_index("uq_raw_ohlcv_daily_symbol_date", "ohlcv_daily", ["symbol", "date"], unique=True, schema="raw")

    # ── screener result tables ────────────────────────────────────────────────
    for timeframe in ("daily", "weekly", "monthly"):
        table_name = f"results_{timeframe}"
        op.create_table(
            table_name,
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("symbol", sa.String(20), nullable=False),
            sa.Column("strategy_name", sa.String(100), nullable=False),
            sa.Column("signal", sa.String(20), nullable=False),
            sa.Column("score", sa.Numeric(5, 4), nullable=False),
            sa.Column("as_of_date", sa.Date, nullable=False),
            sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
            schema="screener",
        )
        op.create_index(
            f"ix_screener_{timeframe}_symbol_date",
            table_name, ["symbol", "as_of_date"],
            schema="screener",
        )
        op.create_index(
            f"ix_screener_{timeframe}_strategy_date",
            table_name, ["strategy_name", "as_of_date"],
            schema="screener",
        )


def downgrade() -> None:
    for timeframe in ("monthly", "weekly", "daily"):
        op.drop_table(f"results_{timeframe}", schema="screener")

    op.drop_table("ohlcv_daily", schema="raw")
    op.drop_table("tickers", schema="raw")
    op.drop_table("watchlist", schema="meta")
    op.drop_table("pipeline_runs", schema="meta")

    op.execute("DROP SCHEMA IF EXISTS screener")
    op.execute("DROP SCHEMA IF EXISTS marts")
    op.execute("DROP SCHEMA IF EXISTS staging")
    op.execute("DROP SCHEMA IF EXISTS raw")
    op.execute("DROP SCHEMA IF EXISTS meta")
