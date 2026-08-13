# Release Guide

## 1. Pre-release checks
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
