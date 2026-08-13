# UV Build and Publish Guide

This guide shows how to build and publish this package using `uv` and a local `.env` file.

## 1. Prepare `.env`

Create a `.env` file in project root:

```env
UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxx
```

Notes:
- Keep `.env` in `.gitignore`.
- Do not share token values in chat, logs, or screenshots.

## 2. Build package

```bash
uv build
```

This creates artifacts in `dist/`.

## 3. Validate artifacts

```bash
uv run python -m twine check dist/*
```

## 4. Dry-run publish (recommended)

```bash
uv run --env-file .env -- uv publish --dry-run --trusted-publishing never
```

This checks auth and upload flow without a real release.

## 5. Publish to PyPI

```bash
uv run --env-file .env -- uv publish --trusted-publishing never
```

Equivalent short command:

```bash
uv run --env-file .env -- uv publish
```

## 6. Optional: publish to TestPyPI

If you want TestPyPI first, set URL variables in `.env`:

```env
UV_PUBLISH_URL=https://test.pypi.org/legacy/
UV_PUBLISH_CHECK_URL=https://test.pypi.org/simple/
```

Then run:

```bash
uv run --env-file .env -- uv publish --trusted-publishing never
```

## 7. Common issues

- `403 Forbidden`: token invalid or missing upload permissions.
- `File already exists`: same version already published. Bump version in `pyproject.toml`.
- `.env` not loaded: ensure command includes `--env-file .env` before `--`.

## 8. Minimal release flow

```bash
uv build
uv run python -m twine check dist/*
uv run --env-file .env -- uv publish --dry-run --trusted-publishing never
uv run --env-file .env -- uv publish --trusted-publishing never
```
