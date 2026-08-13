from __future__ import annotations

from importlib.metadata import entry_points
from typing import Callable

from .models import ModemProfile

DriverFactory = Callable[[ModemProfile], object]


class DriverRegistry:
    def __init__(self) -> None:
        self._drivers: dict[str, DriverFactory] = {}

    def register(self, name: str, driver_factory: DriverFactory, aliases: list[str] | None = None) -> None:
        normalized_name = self._normalize(name)
        self._drivers[normalized_name] = driver_factory
        for alias in aliases or []:
            self._drivers[self._normalize(alias)] = driver_factory

    def get(self, name: str) -> DriverFactory | None:
        return self._drivers.get(self._normalize(name))

    def names(self) -> list[str]:
        return sorted(self._drivers)

    def load_entry_points(self, group: str = "modembridge.drivers") -> list[str]:
        loaded_names: list[str] = []
        for ep in entry_points(group=group):
            try:
                driver_factory = ep.load()
            except Exception:
                continue
            self.register(ep.name, driver_factory)
            loaded_names.append(ep.name)
        return loaded_names

    def _normalize(self, name: str) -> str:
        return name.lower().strip()
