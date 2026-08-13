from __future__ import annotations

from .models import SmsHistoryEntry, SmsSendResult
from .types import ModemDriver


class Modem:
    def __init__(self, driver: ModemDriver) -> None:
        self._driver = driver

    def send_sms(self, phone: str, text: str, retries: int = 3) -> SmsSendResult:
        return self._driver.send_sms(phone, text, retries=retries)

    def get_sms_history(self) -> list[SmsHistoryEntry]:
        return self._driver.get_sms_history()

    def close(self) -> None:
        if hasattr(self._driver, "close"):
            self._driver.close()
