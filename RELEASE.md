# Release Guide

This project is published as the PyPI package `modembridge` under the ToolsyLabs organization.

Package and repo references:

- PyPI: https://pypi.org/project/modembridge/
- Repository: https://github.com/toolsylabs/modembridge
- Organization: https://github.com/toolsylabs

## 1. Pre-release checks
- Check the version in `pyproject.toml` before publishing.
- If the previous version already exists on PyPI, bump the version first.
- Run tests: `python -m unittest discover -s tests -v`
- Build artifacts: `python -m build`
- Validate artifacts: `python -m twine check dist/*`

uv equivalents:
- Run tests: `uv run python -m unittest discover -s tests -v`
- Build artifacts: `uv build`
- Validate artifacts: `uv run python -m twine check dist/*`

## 2. TestPyPI upload
- `python -m twine upload --repository testpypi dist/*`
- Verify installation from TestPyPI in a fresh environment.

uv equivalent:
- `uv run python -m twine upload --repository testpypi dist/*`

## 3. PyPI upload
- `python -m twine upload dist/*`

uv equivalent:
- `uv run python -m twine upload dist/*`

## 4. GitHub release
- Tag version (example): `git tag v0.1.0`
- Push tags: `git push --tags`
- Create release notes from `CHANGELOG.md`.

## 5. Release checklist
- Confirm the version in `pyproject.toml` is correct.
- Review the changelog entries.
- Confirm the package metadata and URLs match the ToolsyLabs repo.
- Use `uv run --env-file .env -- uv publish` for a verified environment-driven upload flow.
