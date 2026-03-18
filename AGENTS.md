# AGENTS.md (Repository Playbook)

Guidance for agentic coding tools operating in `muffin/core`.
Use repository-native commands and conventions.

## Project Snapshot
- Language: Python (`>=3.10`)
- Package/env manager: `uv`
- Build backend: `hatchling`
- Main package: `muffin/`
- Tests: `tests/`
- Example app: `example/`
- Lint/type tools: `ruff`, `pyrefly`
- Test runner: `pytest`
- Commit convention: Conventional Commits (pre-commit enforced)

## Source of Truth
When guidance conflicts, use:
1. `pyproject.toml`
2. `Makefile`
3. `.github/workflows/*.yml`
4. `.pre-commit-config.yaml`
5. Existing patterns in `muffin/` and `tests/`

## Setup Commands (root)
- Install all groups: `uv sync --all-groups`
- Locked CI-like install: `uv sync --locked --all-extras --dev`
- Bootstrap deps/hooks: `make`

## Build / Lint / Test Commands

### Lint + Types
- Lint target: `make lint`
- Direct lint: `uv run ruff check`
- Type check: `uv run pyrefly check`
- Format: `uv run ruff format`

### Tests
- Full suite: `make test`
- Full suite direct: `uv run pytest -xsvl tests`
- CI workflow command: `uv run pytest tests`

### Single Test Commands (important)
- Single file: `uv run pytest -xsvl tests/test_application.py`
- Single test: `uv run pytest -xsvl tests/test_application.py::test_app_config`
- Single class method: `uv run pytest -xsvl tests/test_file.py::TestClass::test_method`
- Keyword filter: `uv run pytest -xsvl tests -k "plugin and not context"`
- Marker filter: `uv run pytest -xsvl tests -m "not slow"`

### Docs
- Build docs: `make docs`
- Direct docs build: `uv run sphinx-build docs/ docs/_build -b html`

### Additional Useful Commands
- Run one test package: `uv run pytest -xsvl tests/common`
- Stop after first failure is already enabled via `-x` in local default options.
- Run with importlib mode (tox pattern): `uv run pytest tests --import-mode importlib`
- Show version: `uv version --short`
- Run all checks manually before commit:
  - `uv run ruff check`
  - `uv run ruff format`
  - `uv run pyrefly check`
  - `uv run pytest -xsvl tests`

## Example App Commands
- From repo root: `make run`, `make shell`
- From `example/`: `make test`, `make run`

## Code Style Guidelines

### Formatting
- Max line length: 100 (Ruff).
- Use `uv run ruff format` on touched files.
- Keep code compact/readable; avoid noisy vertical spacing.
- Preserve local quote/docstring style unless refactor demands change.

### Imports
- Group imports: stdlib, third-party, local.
- Prefer absolute package imports (`from muffin...`).
- Move typing-only imports into `if TYPE_CHECKING:`.
- Remove unused imports (Ruff enforced).

### Types and Annotations
- Use modern typing (`|`, built-in generics like `list[str]`).
- Keep/introduce `from __future__ import annotations` where already used.
- Type public APIs and non-trivial helpers.
- Avoid import cycles with `TYPE_CHECKING` guards.
- Validate with `uv run pyrefly check`.

### Naming
- Classes: `PascalCase`
- Functions/variables/modules: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Tests: files `tests/test_*.py`, functions `test_*`
- Config keys are typically uppercase (`LOG_LEVEL`, `STATIC_URL_PREFIX`)

### Control Flow and Design
- Prefer guard clauses over nested conditionals.
- Keep functions focused on one responsibility.
- Preserve async-first patterns; handlers should be async.
- Keep changes minimal and backward-compatible unless asked otherwise.

### Error Handling
- Raise specific exceptions with actionable messages.
- Use exception chaining (`raise ... from exc`) when wrapping errors.
- Do not swallow exceptions unless behavior requires it (`silent=True` patterns).
- Log failures with concise operational context.

### Logging
- Use `%s` interpolation in logger calls (avoid f-strings in logging methods).
- Reuse app/package logger patterns where possible.

### Testing
- Use clear arrange/act/assert structure.
- Keep async behavior in async tests.
- Reuse fixtures from `tests/conftest.py` and `tests/common/conftest.py`.
- Assert concrete outcomes (status, headers, body/payload).

## Ruff and Pre-commit Notes
- Ruff config uses `select = ["ALL"]` with project-specific ignores.
- Tests have extra per-file ignores; production code should be stricter.
- Pre-commit runs: commit-message checks, Ruff check/format, `uv lock --check`, pyrefly.
- Allowed commit types are in `.git-commits.yaml`.

## Cursor/Copilot Rules
Repository scan results:
- No `.cursorrules` found
- No `.cursor/rules/` found
- No `.github/copilot-instructions.md` found

If these files are added later, treat them as mandatory and update this playbook.

## Recommended Agent Workflow
1. Read `pyproject.toml` and target module(s).
2. Implement minimal focused changes.
3. Run targeted tests first (single file/node id when possible).
4. Run `uv run ruff check` and `uv run pyrefly check`.
5. Run full tests (`uv run pytest -xsvl tests`) for broad or risky changes.

## Safety
- Do not modify unrelated files.
- Do not add dependencies unless required.
- Avoid broad refactors unless requested.
- Preserve public API compatibility in framework code.
