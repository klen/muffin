VIRTUAL_ENV ?= .venv

all: $(VIRTUAL_ENV)


# =============
#  Development
# =============

$(VIRTUAL_ENV): uv.lock .pre-commit-config.yaml
	@echo "Setting up virtual environment and installing dependencies..."
	@uv sync --all-groups
	@GIT_CONFIG=/dev/null && uv run pre-commit install
	@touch $(VIRTUAL_ENV) # Create a marker file

.PHONY: t test
# target: test - Run tests
t test: $(VIRTUAL_ENV)
	@uv run pytest -xsvl --mypy tests

.PHONY: lint
# target: mypy - Run typechecking
lint: $(VIRTUAL_ENV)
	@uv run ruff muffin
	@uv run mypy

.PHONY: mypy
# target: mypy - Run typechecking
mypy: $(VIRTUAL_ENV)
	@uv run mypy

.PHONY: docs
docs: $(VIRTUAL_ENV)
	@uv run sphinx-build docs/ docs/_build -b html
	# @$(VIRTUAL_ENV)/bin/python setup.py upload_sphinx --upload-dir=docs/_build/html


.PHONY: run
run:
	make -C $(CURDIR)/example run

.PHONY: shell
shell:
	make -C $(CURDIR)/example shell

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release: $(VIRTUAL_ENV)
	@git checkout develop
	@git pull
	@git checkout master
	@git pull
	@git merge develop
	@uvx bump-my-version bump $(VERSION)
	@uv lock
	@git commit -am "build(release): `uv version --short`"
	@git tag `uv version --short`
	@git checkout develop
	@git merge master
	@git push --tags origin develop master
	@echo "Release process complete for `uv version --short`."

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major

.PHONY: version v
version v:
	@uv version --short
