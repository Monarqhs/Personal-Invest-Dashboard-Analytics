"""Unit tests for idempotency key generation — no DB required."""
from datetime import date

from shared.utils.idempotency import make_idempotency_key, ohlcv_idempotency_key


def test_idempotency_key_is_deterministic() -> None:
    key1 = make_idempotency_key("BBCA.JK", date(2025, 1, 15))
    key2 = make_idempotency_key("BBCA.JK", date(2025, 1, 15))
    assert key1 == key2


def test_idempotency_key_differs_for_different_inputs() -> None:
    k1 = make_idempotency_key("BBCA.JK", date(2025, 1, 15))
    k2 = make_idempotency_key("BBCA.JK", date(2025, 1, 16))
    k3 = make_idempotency_key("BBRI.JK", date(2025, 1, 15))
    assert k1 != k2
    assert k1 != k3
    assert k2 != k3


def test_ohlcv_key_is_symbol_case_insensitive_normalized() -> None:
    k1 = ohlcv_idempotency_key("bbca.jk", date(2025, 1, 15))
    k2 = ohlcv_idempotency_key("BBCA.JK", date(2025, 1, 15))
    assert k1 == k2


def test_ohlcv_key_is_valid_uuid() -> None:
    import uuid
    key = ohlcv_idempotency_key("AAPL", date(2024, 6, 1))
    assert isinstance(key, uuid.UUID)
    assert key.version == 5
