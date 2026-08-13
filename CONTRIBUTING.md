# Contributing

Thanks for contributing to ModemBridge.

## Development setup
1. Create and activate a virtual environment.
2. Install package and development dependencies:
   - `python -m pip install -e .[dev]`

uv workflow:
- `uv sync`

## Run tests
- `python -m unittest discover -s tests -v`
- `uv run python -m unittest discover -s tests -v`

## Coding guidelines
- Keep core vendor-neutral.
- Put vendor-specific protocol logic inside drivers.
- Do not commit real credentials, IMSI/IMEI, or session tokens.
- Add/adjust tests for any behavior changes.

## Pull requests
- Include a concise summary and testing notes.
- Update `README.md` and `CHANGELOG.md` when behavior changes.
