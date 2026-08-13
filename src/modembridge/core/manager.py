from __future__ import annotations

from .exceptions import DriverNotFoundError
from .models import ModemProfile
from .modem import Modem
from .registry import DriverFactory, DriverRegistry
from ..drivers.zte_goform.driver import ZteGoformDriver


class ModemManager:
    def __init__(self, load_external_drivers: bool = True) -> None:
        self._registry = DriverRegistry()
        self._register_builtin_drivers()
        if load_external_drivers:
            self._registry.load_entry_points()

    def _register_builtin_drivers(self) -> None:
        self._registry.register(
            "zte_goform",
            ZteGoformDriver,
            aliases=["zte", "zte_http", "zte_goform_http"],
        )

    def register_driver(self, name: str, driver_cls: DriverFactory, aliases: list[str] | None = None) -> None:
        self._registry.register(name, driver_cls, aliases=aliases)

    def get_driver_names(self) -> list[str]:
        return self._registry.names()

    def discover(self) -> list[str]:
        return self.get_driver_names()

    def probe(self, profile: ModemProfile) -> bool:
        driver_cls = self._registry.get(profile.name)
        if driver_cls is None:
            return False
        try:
            driver = driver_cls(profile)
        except Exception:
            return False

        probe_method = getattr(driver, "probe", None)
        if callable(probe_method):
            return bool(probe_method())
        return True

    def connect(self, profile: ModemProfile) -> Modem:
        profile.validate()
        driver_cls = self._registry.get(profile.name)
        if driver_cls is None:
            raise DriverNotFoundError(f"Unsupported modem profile: {profile.name}")
        driver = driver_cls(profile)
        return Modem(driver)
