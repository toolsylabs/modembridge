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

    def test_send_status_mapping_distinguishes_accepted_from_delivered(self) -> None:
        profile = ModemProfile(name="zte_goform", host="http://192.168.0.1", password="secret")
        driver = ZteGoformDriver(profile)
        self.assertEqual(driver._describe_sms_send_status("2"), "sending")
        self.assertEqual(driver._describe_sms_send_status("3"), "delivered")
        self.assertEqual(driver._describe_sms_send_status("4"), "failed")

    def test_modem_filters_history_by_id_and_phone(self) -> None:
        profile = ModemProfile(name="zte_goform", host="http://192.168.0.1", password="secret")
        manager = ModemManager(load_external_drivers=False)
        modem = manager.connect(profile)

        entries = [
            type("Entry", (), {"id": "101", "sender": "+998901", "receiver": "+998902", "body": "one", "status": "sent", "direction": "sent"})(),
            type("Entry", (), {"id": "202", "sender": "+998903", "receiver": "+998902", "body": "two", "status": "received", "direction": "received"})(),
            type("Entry", (), {"id": "303", "sender": "+998901", "receiver": "+998904", "body": "three", "status": "sent", "direction": "sent"})(),
        ]

        by_id = [entry for entry in entries if entry.id == "101"]
        by_phone = [entry for entry in entries if entry.direction == "sent" and entry.receiver == "+998902"]

        self.assertEqual(len(by_id), 1)
        self.assertEqual(len(by_phone), 1)
        self.assertEqual(by_phone[0].body, "one")


if __name__ == "__main__":
    unittest.main()
