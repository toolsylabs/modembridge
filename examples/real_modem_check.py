import os

from modembridge import ModemManager, ModemProfile


def main() -> None:
    host = os.environ.get("MODEMBRIDGE_HOST", "http://192.168.0.1")
    password = os.environ.get("MODEMBRIDGE_PASSWORD", "")
    phone = os.environ.get("MODEMBRIDGE_PHONE", "+998901234567")
    text = os.environ.get("MODEMBRIDGE_TEXT", "Test message from ModemBridge")

    if not password:
        raise RuntimeError("MODEMBRIDGE_PASSWORD is not set in environment or .env")

    profile = ModemProfile(
        name="zte_goform",
        host=host,
        username="admin",
        password=password,
    )

    manager = ModemManager()
    print("Probe:")
    print(manager.probe(profile))

    modem = manager.connect(profile)
    try:
        print("\n=== SMS history ===")
        history = modem.get_sms_history()
        print(f"history entries: {len(history)}")
        for entry in history[:5]:
            print(entry)

        print("\n=== Send SMS ===")
        result = modem.send_sms(phone, text)
        print(result)
        print("send_status:", result.details.get("send_status"))
        print("sms_cmd_status_result:", result.details.get("sms_cmd_status_result"))

        print("\n=== Refresh history after send ===")
        history_after = modem.get_sms_history()
        print(f"history entries after send: {len(history_after)}")
        for entry in history_after[:5]:
            print(entry)

        if history_after:
            last = history_after[0]
            print("\n=== Get by ID ===")
            print(modem.get_sms_by_id(last.id))

            print("\n=== Get by phone ===")
            sent_items = modem.get_sms_by_phone(phone, direction="sent")
            print(sent_items)

    finally:
        modem.close()
        print("\n=== closed ===")


if __name__ == "__main__":
    main()
