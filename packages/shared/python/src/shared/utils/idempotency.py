"""Idempotency key helpers — deterministic UUIDs for upsert operations."""
import hashlib
import uuid
from datetime import date


def make_idempotency_key(*parts: str | date) -> uuid.UUID:
    """Deterministic UUID v5 from ordered string parts.

    Example: make_idempotency_key("BBCA.JK", date(2025, 1, 15))
    Returns the same UUID every time for the same inputs — safe to use as PK for upserts.
    """
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # URL namespace
    key = ":".join(str(p) for p in parts)
    return uuid.uuid5(namespace, key)


def ohlcv_idempotency_key(symbol: str, trading_date: date) -> uuid.UUID:
    return make_idempotency_key("ohlcv", symbol.upper(), trading_date)
