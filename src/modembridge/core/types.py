from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import SmsHistoryEntry, SmsSendResult


@runtime_checkable
class ModemDriver(Protocol):
    def send_sms(self, phone: str, text: str, retries: int = 3) -> SmsSendResult:
        ...

    def get_sms_history(self) -> list[SmsHistoryEntry]:
        ...

    def close(self) -> None:
        ...

    def probe(self) -> bool:
        ...
