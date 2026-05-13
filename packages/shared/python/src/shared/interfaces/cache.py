from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    """Key-value cache abstraction. MVP: in-process LRU. Future: Upstash Redis."""

    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...
