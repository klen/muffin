# Changelog

## 2026-10-29

- asyncio is now the default async library; curio and trio run only when selected via `--aiolib` or `MUFFIN_AIOLIB`.
- A declared handler method without an implementation now fails at class definition instead of returning a 500 response.
- Host-based routing: `USE_HOSTS` option and `hosts=` on routes, including class-based handlers and their sub-routes (requires `asgi-tools>=3.2.0`).
- Environment variables now override plugin options, matching the application's precedence (options are treated as defaults).
- Handler classes require `methods` to be set explicitly or inherited; automatic detection from defined async methods is removed.
- Background task failures are logged instead of tearing down the already-sent response and the keep-alive connection.
- Unknown CLI arguments are rejected instead of silently ignored.
- `Application.import_submodules` resolves the package from the caller module even when called from inside a function.
- A disabled plugin is no longer left half-attached: its `app` property raises `PluginNotInstalledError`.
- `import_app` falls back with explicit `None` checks instead of truthiness.
- `Manager.command` alias removed.

## 2026-06-26

- Drop Python 3.10 support. Minimum required version is now Python 3.11.

## 2026-03-19

- Logging for command execution in `Manager.run`.

## 2026-03-18

- Updated `asgi-tools` dependency.
- `request.form` now supports only `max_size` (no `file_memory_limit`).

## 2026-03-02

- `manage` type-argument handling for Python 3.14.
- Internal bugfixes and maintenance updates.

## 2026-02-12

- Plugin `conftest` lifecycle integration.
- Improved typing coverage.
- Build and release maintenance fixes.
- Type system tuning and internal refactoring.
- Internal bugfixes and maintenance updates.

## 2025-11-06

- Python 3.14 support.

## 2025-07-21

- Updated `asgi-tools` to `1.3.3`.

## 2025-07-17

- Error handling in `manage.py`.
- Exception handling behavior in `manage.py`.
- Deterministic CLI help output via subparser sorting by name.
- CLI command execution exception handling.

## 2025-07-11

- Documentation structure and README updates.
- Dependency synchronization and Sphinx configuration updates.
- Updated supported Python versions and removed obsolete project files.
- Refined plugin type hints and pre-commit/commit configuration.

## 2024-07-31

- Internal maintenance updates.
- Python 3.9 support.
- Python 3.12 support.
- Drop Python 3.8 support.

## 2023-03-04

- Drop Python 3.7 support.

## 2022-04-06

- Update `modconfig` to `1.2.1`.

## 2022-02-09

- Follow asgi-tools 0.64.1.

## 2021-12-14

- Fix closing websockets.

## 2015-02-09

- First public release
