# Driver Guide

This project is designed to grow with additional modem drivers.

## Can we keep adding new modem types?

Yes. The architecture is intentionally driver-based, so new modem families can be added over time without changing the core API.

Examples of future targets:

- USB GSM/LTE/5G modems
- Serial AT-command modems
- WebUI/API modems (ZTE Goform, Huawei HiLink, and similar)
- LAN/Wi-Fi cellular routers and SMS gateways

Practical note:

- A modem is addable when it exposes a usable interface (HTTP API, serial AT, or equivalent).
- The current `ModemProfile` validation in core is URL-oriented (`http`/`https` host). Serial-focused workflows may require a profile extension in future releases.

## Driver contract

A driver should provide:

- `send_sms(phone: str, text: str, retries: int = 3)`
- `get_sms_history()`
- Optional: `probe()` for capability/device checks
- Optional: `close()` for connection cleanup

You can reference the protocol type in code:

- `modembridge.ModemDriver`

## Registering a driver programmatically

```python
from modembridge import ModemManager

manager = ModemManager(load_external_drivers=False)
manager.register_driver("my_driver", MyDriver, aliases=["my_vendor"])
```

## Registering via entry points (recommended for external packages)

In your external package `pyproject.toml`:

```toml
[project.entry-points."modembridge.drivers"]
my_driver = "my_package.driver:MyDriver"
```

`ModemManager()` auto-loads entry points from the `modembridge.drivers` group by default.

## Suggested structure for new drivers

- Keep protocol and parsing logic inside driver module.
- Keep core vendor-neutral.
- Avoid leaking vendor-specific details in public API.
- Add tests for auth flow, send flow, and parser semantics.
