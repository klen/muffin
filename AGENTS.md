# AGENTS

## Fast start (authoritative commands)

- Install/update dev env: `make` (runs `uv sync --all-groups` and installs pre-commit hooks).
- Lint + typecheck: `make lint` (runs `ruff check` then `pyrefly check`).
- Tests: `make test` (equivalent to `uv run pytest -xsvl tests`).
- Docs build: `make docs` (Sphinx HTML into `docs/_build`).

## Verification order used by CI

- Match CI locally: `uv run ruff check` -> `uv run pyrefly check` -> `uv run pytest tests`.
- CI uses Python `3.10`-`3.14` (`.github/workflows/tests.yml`).

## Repo shape and real entrypoints

- Core package is `muffin/` (single-package repo, not a monorepo).
- Public API exports come from `muffin/__init__.py`.
- Main framework class is `muffin/app.py` (`Application`).
- CLI entrypoint is the `muffin` script -> `muffin.manage:cli` (`pyproject.toml`).
- Pytest plugin is built-in via entry point `muffin.pytest`.
- `example/` is a git submodule (`.gitmodules`), not core framework code.

## Testing and async quirks

- Pytest default app is configured as `muffin_app = "tests:app"` in `pyproject.toml`;
  tests rely on `tests/__init__.py` app fixture.
- Project-level `tests/conftest.py` parametrizes `aiolib` across `asyncio`, `asyncio+uvloop`,
  `trio`, `curio`, so async tests can run multiple times per backend.
- For focused runs, use node selection directly,
  e.g. `uv run pytest tests/test_application.py::test_app_config`.

## Config/env details agents usually miss

- App config env var is `MUFFIN_CONFIG` (`muffin/constants.py`),
  used by both app init and CLI `--config`.
- Async backend can be forced with `MUFFIN_AIOLIB` (`muffin/utils.py`).

## Hooks and commit conventions

- Pre-commit enforces Conventional Commits using `.git-commits.yaml` (allowed types include `feat`,
  `fix`, `refactor`, `test`, etc.).
- `uv.lock` consistency is enforced by pre-commit (`uv-lock --check`);
  update lockfile when dependency groups change.
- Pre-push hook runs `poetry run pytest tests` from `.pre-commit-config.yaml` (note:
  repo otherwise uses `uv`).

## Release workflow safety

- `make release` is branch-opinionated and mutates git state:
  checks out/pulls `master` and `develop`, bumps version, tags, merges both ways, and pushes.
- Do not run release targets for normal feature work.
