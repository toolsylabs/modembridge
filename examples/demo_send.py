import os

from modembridge import ModemManager, ModemProfile


if __name__ == "__main__":
    host = os.environ.get("MODEMBRIDGE_HOST", "http://192.168.0.1")
    password = os.environ.get("MODEMBRIDGE_PASSWORD", "")
    phone = os.environ.get("MODEMBRIDGE_PHONE", "+123456789")
    text = os.environ.get("MODEMBRIDGE_TEXT", "Hello from ModemBridge")

    profile = ModemProfile(
        name="zte_goform",
        host=host,
        username="admin",
        password=password,
    )
    manager = ModemManager()
    modem = manager.connect(profile)
    result = modem.send_sms(phone, text)
    print(result)
    modem.close()
