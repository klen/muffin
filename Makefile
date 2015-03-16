VIRTUALENV=$(shell echo "$${VDIR:-'.env'}")

all: $(VIRTUALENV)

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
	@$(VIRTUALENV)/bin/pip install bumpversion
	@$(VIRTUALENV)/bin/bumpversion $(VERSION)
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
	@$(VIRTUALENV)/bin/python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@$(VIRTUALENV)/bin/pip install twine wheel
	@$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel
	@$(VIRTUALENV)/bin/twine upload dist/*

# =============
#  Development
# =============

$(VIRTUALENV): requirements.txt
	@[ -d $(VIRTUALENV) ] || virtualenv --no-site-packages $(VIRTUALENV)
	@$(VIRTUALENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUALENV)

$(VIRTUALENV)/bin/py.test: $(VIRTUALENV) requirements-tests.txt
	@$(VIRTUALENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUALENV)/bin/py.test

.PHONY: test
# target: test - Runs tests
test: $(VIRTUALENV)/bin/py.test
	@$(VIRTUALENV)/bin/py.test tests

.PHONY: t
t: test

.PHONY: doc
doc: docs $(VIRTUALENV)
	@$(VIRTUALENV)/bin/pip install sphinx
	@$(VIRTUALENV)/bin/pip install sphinx-pypi-upload
	@$(VIRTUALENV)/bin/python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	@$(VIRTUALENV)/bin/python setup.py upload_sphinx --upload-dir=docs/_build/html


MANAGER=$(VIRTUALENV)/bin/muffin example.app:app
CMD = --help

.PHONY: manage
manage: $(VIRTUALENV)
	@$(MANAGER) $(CMD)

.PHONY: run
run: $(VIRTUALENV) db.sqlite
	@make manage CMD=run

.PHONY: shell
shell: $(VIRTUALENV)
	@make manage CMD=shell

.PHONY: db
db: db.sqlite

db.sqlite: $(VIRTUALENV)
	@$(VIRTUALENV)/bin/muffin example.app:app migrate
