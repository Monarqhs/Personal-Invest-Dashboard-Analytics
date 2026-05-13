"""Timezone helpers — UTC is canonical in DB; WIB (Asia/Jakarta) at presentation only."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")
UTC = ZoneInfo("UTC")


def wib_now() -> datetime:
    return datetime.now(tz=WIB)


def wib_today() -> date:
    return wib_now().date()


def to_utc(dt: datetime) -> datetime:
    """Convert any tz-aware datetime to UTC. Raises if dt is naive."""
    if dt.tzinfo is None:
        raise ValueError(f"Cannot convert naive datetime to UTC: {dt!r}")
    return dt.astimezone(UTC)
