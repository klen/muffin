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

RELEASE	?= minor
MANAGER	?= uv

.PHONY: release
# target: release - Bump version
release:
	@echo "Starting release process (bumping $(RELEASE) version)..."
	@git checkout main
	@git pull
	@git checkout develop
	@git pull
	@echo "Bumping version and creating release commit and tag..."
	@uvx bump-my-version bump $(RELEASE)
	@echo "Version bumped to `$(MANAGER) version --short`."
	@$(MANAGER) lock
	@echo "Committing version bump and creating tag..."
	@VERSION=`$(MANAGER) version --short`; \
		{ \
			printf 'build(release): %s\n\n' "$$VERSION"; \
			printf 'Changes:\n\n'; \
			git log --oneline --pretty=format:'%s [%an]' main..develop | grep -Evi 'github|^Merge' || true; \
		} | git commit -a -F -
	@echo "Merging changes between branches..."
	@git checkout main
	@git merge --ff-only develop
	@VERSION=`$(MANAGER) version --short`; \
		git push origin main; \
		git tag -a "$$VERSION" -m "$$VERSION"; \
		git push origin "$$VERSION"
	@git checkout develop
	@git merge --ff-only main
	@git push origin develop
	@echo "Release process complete for `$(MANAGER) version --short`"

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release RELEASE=patch

.PHONY: major
major:
	make release RELEASE=major

version v:
	uv version --short
