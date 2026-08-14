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

    def get_sms_by_id(self, message_id: str) -> SmsHistoryEntry | None:
        for entry in self.get_sms_history():
            if str(entry.id) == str(message_id):
                return entry
        return None

    def get_sms_by_phone(self, phone: str, direction: str | None = None) -> list[SmsHistoryEntry]:
        target_phone = phone.strip()
        results: list[SmsHistoryEntry] = []
        for entry in self.get_sms_history():
            matches = False
            if entry.sender == target_phone or entry.receiver == target_phone:
                matches = True
            if direction is not None and entry.direction.lower() != direction.lower():
                matches = False
            if matches:
                results.append(entry)
        return results

    def close(self) -> None:
        if hasattr(self._driver, "close"):
            self._driver.close()
