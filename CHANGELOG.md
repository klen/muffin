# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.0] - 2026-03-19

### Added

- Logging for command execution in `Manager.run`.

## [1.5.1] - 2026-03-18

### Changed

- Updated `asgi-tools` dependency.
- `request.form` now supports only `max_size` (no `file_memory_limit`).

### Removed

- `request.form(file_memory_limit=...)` support.

## [1.4.4] - 2026-03-02

### Fixed

- `manage` type-argument handling for Python 3.14.

## [1.4.3] - 2026-03-02

### Fixed

- Internal bugfixes and maintenance updates.

## [1.4.2] - 2026-02-12

### Fixed

- Internal bugfixes and maintenance updates.

## [1.4.1] - 2026-02-12

### Fixed

- Plugin `conftest` lifecycle integration.

## [1.4.0] - 2026-02-12

### Changed

- Improved typing coverage.

## [1.3.1] - 2026-02-12

### Fixed

- Build and release maintenance fixes.

## [1.3.0] - 2026-02-12

### Changed

- Type system tuning and internal refactoring.

## [1.2.0] - 2025-11-06

### Added

- Python 3.14 support.

## [1.1.4] - 2025-07-21

### Changed

- Updated `asgi-tools` to `1.3.3`.

## [1.1.3] - 2025-07-17

### Fixed

- Error handling in `manage.py`.

## [1.1.2] - 2025-07-17

### Changed

- Exception handling behavior in `manage.py`.

## [1.1.1] - 2025-07-17

### Added

- Deterministic CLI help output via subparser sorting by name.

## [1.1.0] - 2025-07-17

### Fixed

- CLI command execution exception handling.

## [1.0.2] - 2025-07-11

### Changed

- Documentation structure and README updates.

## [1.0.1] - 2025-07-11

### Changed

- Dependency synchronization and Sphinx configuration updates.

## [1.0.0] - 2025-07-11

### Changed

- Updated supported Python versions and removed obsolete project files.
- Refined plugin type hints and pre-commit/commit configuration.

## [0.102.3] - 2024-07-31

### Changed

- Internal maintenance updates.

## [0.102.2] - 2024-07-31

### Changed

- Internal maintenance updates.

## [0.102.1] - 2024-07-31

### Added

- Python 3.9 support.

## [0.102.0] - 2024-07-31

### Added

- Python 3.12 support

### Removed

- Drop Python 3.8 support

## [0.92.0] - 2023-03-04

### Removed

- Drop Python 3.7 support

## [0.87.1] - 2022-04-06

### Changed

- Update `modconfig` to `1.2.1`.

## [0.87.0] - 2022-02-09

### Changed

- Follow asgi-tools 0.64.1

## [0.86.2] - 2021-12-14

### Changed

- Fix closing websockets

## [0.0.1] - 2015-02-09

- First public release

[unreleased]: https://github.com/klen/muffin/compare/1.6.0...HEAD
[1.6.0]: https://github.com/klen/muffin/compare/1.5.1...1.6.0
[1.5.1]: https://github.com/klen/muffin/compare/1.5.0...1.5.1
[1.5.0]: https://github.com/klen/muffin/compare/1.4.4...1.5.0
[1.4.4]: https://github.com/klen/muffin/compare/1.4.3...1.4.4
[1.4.3]: https://github.com/klen/muffin/compare/1.4.2...1.4.3
[1.4.2]: https://github.com/klen/muffin/compare/1.4.1...1.4.2
[1.4.1]: https://github.com/klen/muffin/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/klen/muffin/compare/1.3.1...1.4.0
[1.3.1]: https://github.com/klen/muffin/compare/1.3.0...1.3.1
[1.3.0]: https://github.com/klen/muffin/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/klen/muffin/compare/1.1.4...1.2.0
[1.1.4]: https://github.com/klen/muffin/compare/1.1.3...1.1.4
[1.1.3]: https://github.com/klen/muffin/compare/1.1.2...1.1.3
[1.1.2]: https://github.com/klen/muffin/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/klen/muffin/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/klen/muffin/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/klen/muffin/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/klen/muffin/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/klen/muffin/compare/0.102.3...1.0.0
[0.102.3]: https://github.com/klen/muffin/compare/0.102.2...0.102.3
[0.102.2]: https://github.com/klen/muffin/compare/0.102.1...0.102.2
[0.102.1]: https://github.com/klen/muffin/compare/0.102.0...0.102.1
[0.102.0]: https://github.com/klen/muffin/compare/0.92.0...0.102.0
[0.92.0]: https://github.com/klen/muffin/compare/0.87.1...0.92.0
[0.87.1]: https://github.com/klen/muffin/compare/0.87.0...0.87.1
[0.87.0]: https://github.com/klen/muffin/compare/0.86.2...0.87.0
[0.86.2]: https://github.com/klen/muffin/compare/0.1.0...0.86.2
[0.1.0]: https://github.com/klen/muffin/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/klen/muffin/releases/tag/0.0.1
