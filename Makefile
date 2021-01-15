VIRTUAL_ENV ?= env

all: $(VIRTUAL_ENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@$(VIRTUAL_ENV)/bin/pip install bump2version
	@$(VIRTUAL_ENV)/bin/bump2version $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push origin develop master
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major

# ===============
#  Build package
# ===============

.PHONY: register
# target: register - Register module on PyPi
register:
	@$(VIRTUAL_ENV)/bin/python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@$(VIRTUAL_ENV)/bin/pip install twine wheel
	@$(VIRTUAL_ENV)/bin/python setup.py bdist_wheel
	@$(VIRTUAL_ENV)/bin/twine upload dist/*

# =============
#  Development
# =============

$(VIRTUAL_ENV): requirements.txt setup.cfg
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

.PHONY: t test
# target: test - Run tests
t test: $(VIRTUAL_ENV)/bin/py.test
	@$(VIRTUAL_ENV)/bin/py.test tests

.PHONY: doc
doc: docs $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install sphinx
	@$(VIRTUAL_ENV)/bin/pip install sphinx-pypi-upload
	@$(VIRTUAL_ENV)/bin/python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	# @$(VIRTUAL_ENV)/bin/python setup.py upload_sphinx --upload-dir=docs/_build/html


.PHONY: run
run:
	make -C $(CURDIR)/example run

.PHONY: shell
shell:
	make -C $(CURDIR)/example shell

