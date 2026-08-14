# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-08-14
- Fixed `.env` parsing warnings by quoting values that contain spaces.
- Bumped package version because `0.1.0` already existed on PyPI.
- Refreshed project documentation to match the live ZTE hardware validation findings.
- Clarified that a successful SMS send response is request acceptance, not final delivery confirmation.
- Updated PyPI and repository references to the current ToolsyLabs ownership and package metadata.

## [0.1.0] - 2026-08-13
- Initial public alpha of ModemBridge.
- Added extensible manager + driver registry.
- Added first real driver: ZTE Goform HTTP modem.
- Added SMS send and SMS history APIs.
- Added CLI entry point (`modembridge`).
- Added package metadata and release docs for GitHub/PyPI.
- Updated project ownership metadata after repository migration to ToolsyLabs (`https://github.com/toolsylabs/modembridge`).
