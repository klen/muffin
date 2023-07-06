VIRTUAL_ENV ?= .venv

all: $(VIRTUAL_ENV)


# =============
#  Development
# =============

$(VIRTUAL_ENV): pyproject.toml
	@poetry install --with dev -E standard
	@poetry run pre-commit install --hook-type pre-push
	@touch $(VIRTUAL_ENV)

.PHONY: t test
# target: test - Run tests
t test: $(VIRTUAL_ENV)
	@poetry run pytest -xsvl --mypy tests

.PHONY: lint
# target: mypy - Run typechecking
lint: $(VIRTUAL_ENV)
	@poetry run ruff muffin
	@poetry run mypy

.PHONY: mypy
# target: mypy - Run typechecking
mypy: $(VIRTUAL_ENV)
	@poetry run mypy

.PHONY: docs
docs: $(VIRTUAL_ENV)
	@poetry run sphinx-build docs/ docs/_build -b html
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
	@git checkout master
	@git merge develop
	@git pull
	@git checkout develop
	@git pull
	@$(eval VFROM := $(shell poetry version -s))
	@poetry version $(VERSION)
	@git commit -am "Bump version $(VFROM) → `poetry version -s`"
	@git tag `poetry version -s`
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push --tags origin develop master

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major
