from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from .exceptions import ModemConfigurationError


@dataclass(slots=True)
class ModemProfile:
    name: str
    transport: str = "http"
    host: str = "http://192.168.0.1"
    username: str = "admin"
    password: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.name:
            raise ModemConfigurationError("Profile name is required")
        if self.transport not in {"http", "https"}:
            raise ModemConfigurationError("Transport must be 'http' or 'https'")
        parsed = urlparse(self.host)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ModemConfigurationError("Host must be a valid URL")


@dataclass(slots=True)
class SmsSendResult:
    ok: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SmsHistoryEntry:
    id: str
    sender: str
    receiver: str
    body: str
    status: str
    direction: str
    raw: dict[str, Any] = field(default_factory=dict)
