from __future__ import annotations

import argparse
import sys

from . import ModemManager, ModemProfile
from . import __version__


def main() -> int:
    parser = argparse.ArgumentParser(description="Send SMS via ModemBridge")
    parser.add_argument("--version", action="version", version=f"modembridge {__version__}")
    parser.add_argument("--host", default="http://192.168.0.1")
    parser.add_argument("--transport", default="http")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="")
    parser.add_argument("--phone")
    parser.add_argument("--text")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--driver", default="zte_goform")
    args = parser.parse_args()

    if not args.history and not args.phone:
        parser.error("--phone is required unless --history is used")
    if not args.history and not args.text:
        parser.error("--text is required unless --history is used")

    profile = ModemProfile(
        name=args.driver,
        host=args.host,
        transport=args.transport,
        username=args.username,
        password=args.password,
    )
    manager = ModemManager()
    modem = manager.connect(profile)

    try:
        if args.history:
            history = modem.get_sms_history()
            print(f"history entries: {len(history)}")
            for entry in history[:5]:
                print(entry)
        else:
            result = modem.send_sms(args.phone, args.text, retries=args.retries)
            print(result)
    finally:
        modem.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
