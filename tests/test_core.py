from __future__ import annotations

import unittest

from modembridge import ModemManager, ModemProfile
from modembridge.core.exceptions import ModemConfigurationError
from modembridge.core.modem import Modem
from modembridge.drivers.zte_goform.driver import ZteGoformDriver


class DummyDriver:
    def __init__(self, profile: ModemProfile) -> None:
        self.profile = profile

    def send_sms(self, phone: str, text: str, retries: int = 3) -> None:
        return None

    def get_sms_history(self) -> list[object]:
        return []

    def close(self) -> None:
        return None

    def probe(self) -> bool:
        return True


class ModemBridgeCoreTests(unittest.TestCase):
    def test_manager_connects_zte_profile(self) -> None:
        profile = ModemProfile(name="zte_goform", host="http://192.168.0.1", password="secret")
        manager = ModemManager(load_external_drivers=False)
        modem = manager.connect(profile)
        self.assertIsInstance(modem, Modem)

    def test_profile_defaults(self) -> None:
        profile = ModemProfile(name="zte_goform")
        self.assertEqual(profile.transport, "http")
        self.assertEqual(profile.host, "http://192.168.0.1")

    def test_driver_hash_helpers(self) -> None:
        profile = ModemProfile(name="zte_goform", password="secret")
        driver = ZteGoformDriver(profile)
        password_hash = driver._build_login_password("secret", "LD")
        ad_value = driver._build_ad_value("rd0", "rd1", "RD")
        self.assertTrue(password_hash)
        self.assertTrue(ad_value)
        self.assertTrue(password_hash.isupper())
        self.assertTrue(ad_value.isupper())

    def test_manager_resolves_aliases(self) -> None:
        profile = ModemProfile(name="zte", host="http://192.168.0.1", password="secret")
        manager = ModemManager(load_external_drivers=False)
        modem = manager.connect(profile)
        self.assertIsInstance(modem, Modem)

    def test_manager_registers_custom_driver(self) -> None:
        manager = ModemManager(load_external_drivers=False)
        manager.register_driver("dummy", DummyDriver)
        profile = ModemProfile(name="dummy", host="http://example.test")
        modem = manager.connect(profile)
        self.assertIsInstance(modem, Modem)

    def test_manager_discovers_registered_drivers(self) -> None:
        manager = ModemManager(load_external_drivers=False)
        manager.register_driver("dummy", DummyDriver)
        self.assertIn("dummy", manager.discover())

    def test_manager_probe_for_registered_driver(self) -> None:
        manager = ModemManager(load_external_drivers=False)
        manager.register_driver("dummy", DummyDriver)
        profile = ModemProfile(name="dummy", host="http://example.test")
        self.assertTrue(manager.probe(profile))

    def test_profile_validation_rejects_invalid_host(self) -> None:
        profile = ModemProfile(name="zte", host="not-a-url")
        with self.assertRaises(ModemConfigurationError):
            profile.validate()


if __name__ == "__main__":
    unittest.main()
