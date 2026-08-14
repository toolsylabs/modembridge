# ModemBridge

ModemBridge is an extensible Python SDK for cellular modems and SMS gateway devices.

It provides a unified API for SMS operations while keeping protocol-specific logic inside drivers.

## Status

- Project maturity: alpha (`0.1.0`)
- First real driver: ZTE Goform HTTP modem
- Verified baseline: real-device login, SMS send request, SMS history retrieval, and ID/phone lookup on a live ZTE gateway
- Important nuance: `SEND_SMS` returns a request-accepted signal, not final delivery confirmation; the modem’s status endpoint must be checked separately

## Features

- Unified API for sending SMS and reading SMS history
- Driver registry with alias support
- Vendor-specific protocol handling isolated in drivers
- CLI entry point for quick usage (`modembridge`)
- Release-ready packaging for GitHub and PyPI

## Install

```bash
python -m pip install modembridge
```

With uv:

```bash
uv add modembridge
```

For local development:

```bash
python -m pip install -e .[dev]
```

With uv for this repository:

```bash
uv sync
```

## Quick start (Python)

```python
from modembridge import ModemManager, ModemProfile

profile = ModemProfile(
    name="zte_goform",
    host="http://192.168.0.1",
    username="admin",
    password="your-password",
)

manager = ModemManager()
modem = manager.connect(profile)

try:
    result = modem.send_sms("+998901234567", "Hello from ModemBridge")
    print(result)
finally:
    modem.close()
```

## CLI

Send SMS:

```bash
modembridge --host http://192.168.0.1 --password your-password --phone +998901234567 --text "Hello"
```

Read history:

```bash
modembridge --host http://192.168.0.1 --password your-password --history
```

## SMS lookup patterns

You can fetch an SMS by its modem ID or filter by phone number when you need to identify a specific sent message.

```python
from modembridge import ModemManager, ModemProfile

profile = ModemProfile(
    name="zte_goform",
    host="http://192.168.0.1",
    username="admin",
    password="your-password",
)

manager = ModemManager()
modem = manager.connect(profile)

one = modem.get_sms_by_id("42")
print(one)

sent_to = modem.get_sms_by_phone("+998901234567", direction="sent")
print(sent_to)

modem.close()
```

This is useful when you need to confirm whether a specific SMS was sent and to which number it was sent.

## Real modem validation

The project has been validated against a live ZTE Goform modem using the configured modem password from environment variables.

```bash
uv run --env-file .env python examples/real_modem_check.py
```

Observed live-device behavior:

- `probe()` returned `True` on the real modem
- `get_sms_history()` returned real SMS entries from the modem
- `send_sms()` returned `ok=True` with a request-accepted result
- the modem reported `sms_cmd_status_result=1` immediately after send, which maps to `queued` rather than final delivery
- `get_sms_by_id()` and `get_sms_by_phone()` successfully returned the just-sent message from history

This confirms that the SDK works with the live device and that delivery status must be checked separately from the immediate send response.

## Architecture

ModemBridge keeps core and driver concerns separate:

1. Core: profile model, manager, modem abstraction
2. Driver: protocol-specific login, payloads, and parsers
3. Registry: driver lookup and aliases

Current included driver:

- `zte_goform`

### Adding new drivers (future-proof workflow)

1. Implement a driver class that supports:
    - `send_sms(phone, text, retries=3)`
    - `get_sms_history()`
    - optional `probe()`
    - optional `close()`
2. Register manually:

```python
from modembridge import ModemManager

manager = ModemManager(load_external_drivers=False)
manager.register_driver("my_driver", MyDriver, aliases=["my_vendor"])
```

3. Or register via Python entry points in your separate package:

```toml
[project.entry-points."modembridge.drivers"]
my_driver = "my_package.driver:MyDriver"
```

When `ModemManager()` starts, external drivers from `modembridge.drivers` entry-point group are auto-loaded.

For a focused walkthrough, see `DRIVER_GUIDE.md`.

## Security and privacy

- Never commit real passwords, IMSI/IMEI, SIM numbers, or session cookies.
- Use environment variables or secret managers for runtime credentials.
- Keep logs and bug reports sanitized.

See `SECURITY.md` for reporting guidance.

## Development

Run tests:

```bash
python -m unittest discover -s tests -v
```

With uv:

```bash
uv run python -m unittest discover -s tests -v
```

Build package:

```bash
python -m build
python -m twine check dist/*
```

With uv:

```bash
uv build
uv run python -m twine check dist/*
```

## Releasing

Release steps are documented in `RELEASE.md`.
For `uv` + `.env` publish flow, see `docs/uv-publish.md`.

## Package

- PyPI: https://pypi.org/project/modembridge/

## Creator

- Name: SaidAbbos Khudoykulov
- Email: abbos.xudoyqulov@gmail.com
- Personal GitHub: https://github.com/SaidAbbos96
- Organization: ToolsyLabs
- Organization GitHub: https://github.com/toolsylabs
- Organization Website: https://toolsy.fyi
- Repository: https://github.com/toolsylabs/modembridge

## License

MIT. See `LICENSE`.
