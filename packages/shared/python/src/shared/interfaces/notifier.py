from abc import ABC, abstractmethod
from enum import StrEnum


class NotificationLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Notifier(ABC):
    """Abstraction over notification channels. First impl: Telegram. Drop-in: Discord, Slack, email."""

    @abstractmethod
    async def send(
        self,
        title: str,
        body: str,
        level: NotificationLevel = NotificationLevel.INFO,
    ) -> None: ...
