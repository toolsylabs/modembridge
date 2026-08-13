import os

from modembridge import ModemManager, ModemProfile


if __name__ == "__main__":
    host = os.environ.get("MODEMBRIDGE_HOST", "http://192.168.0.1")
    password = os.environ.get("MODEMBRIDGE_PASSWORD", "")

    profile = ModemProfile(
        name="zte_goform",
        host=host,
        username="admin",
        password=password,
    )
    manager = ModemManager()
    modem = manager.connect(profile)
    history = modem.get_sms_history()
    print(f"history entries: {len(history)}")
    for entry in history[:5]:
        print(entry)
    modem.close()
