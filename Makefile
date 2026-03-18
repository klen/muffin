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
	@uv run pytest -xsvl tests

.PHONY: lint
# target: lint - Run typechecking
lint: $(VIRTUAL_ENV)
	@uv run ruff check
	@uv run pyrefly check

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

VERSION	?= minor
MAIN_BRANCH = master

.PHONY: release
# target: release - Bump version
release:
	git checkout $(MAIN_BRANCH)
	git pull
	git checkout develop
	git pull
	uvx bump-my-version bump $(VERSION)
	uv lock
	@CVER="$$(uv version --short)"; \
		{ \
			printf 'build(release): %s\n\n' "$$CVER"; \
			printf 'Changes:\n\n'; \
			git log --oneline --pretty=format:'%s [%an]' $(MAIN_BRANCH)..develop | grep -Evi 'github|^Merge' || true; \
		} | git commit -a -F -; \
		git tag -a "$$CVER" -m "$$CVER";
	@echo "Merging changes between branches..."
	git checkout $(MAIN_BRANCH)
	git merge develop
	git checkout develop
	git merge $(MAIN_BRANCH)
	@git -c push.followTags=false push origin develop $(MAIN_BRANCH)
	@git push --tags origin
	@echo "Release process complete for `uv version --short`"

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major

version v:
	uv version --short
