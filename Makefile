VIRTUAL_ENV=$(shell echo "$${VDIR:-'.env'}")

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
	@$(VIRTUAL_ENV)/bin/pip install bumpversion
	@$(VIRTUAL_ENV)/bin/bumpversion $(VERSION)
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
	@$(VIRTUAL_ENV)/bin/python setup.py sdist bdist_wheel
	@$(VIRTUAL_ENV)/bin/twine upload dist/*
	@$(VIRTUAL_ENV)/bin/pip install -e $(CURDIR)

# =============
#  Development
# =============

$(VIRTUAL_ENV): requirements.txt
	@[ -d $(VIRTUAL_ENV) ] || virtualenv --no-site-packages $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

$(VIRTUAL_ENV)/bin/muffin: $(VIRTUAL_ENV) requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/muffin

.PHONY: test
# target: test - Runs tests
test: $(VIRTUAL_ENV)/bin/py.test
	@$(VIRTUAL_ENV)/bin/py.test tests

.PHONY: t
t: test

.PHONY: tp
tp:
	@echo 'Test Muffin-Admin'
	@make -C $(CURDIR)/plugins/muffin-admin t
	@echo 'Test Muffin-Jade'
	@make -C $(CURDIR)/plugins/muffin-jade t
	@echo 'Test Muffin-Jinja2'
	@make -C $(CURDIR)/plugins/muffin-jinja2 t
	@echo 'Test Muffin-Mongo'
	@make -C $(CURDIR)/plugins/muffin-mongo t
	@echo 'Test Muffin-OAuth'
	@make -C $(CURDIR)/plugins/muffin-oauth t
	@echo 'Test Muffin-Peewee'
	@make -C $(CURDIR)/plugins/muffin-peewee t
	@echo 'Test Muffin-REST'
	@make -C $(CURDIR)/plugins/muffin-rest t
	@echo 'Test Muffin-Redis'
	@make -C $(CURDIR)/plugins/muffin-redis t
	@echo 'Test Muffin-Sentry'
	@make -C $(CURDIR)/plugins/muffin-sentry t
	@echo 'Test Muffin-Session'
	@make -C $(CURDIR)/plugins/muffin-session t

.PHONY: doc
doc: docs $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install sphinx
	@$(VIRTUAL_ENV)/bin/pip install sphinx-pypi-upload
	@$(VIRTUAL_ENV)/bin/python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	@$(VIRTUAL_ENV)/bin/python setup.py upload_sphinx --upload-dir=docs/_build/html


MANAGER=$(VIRTUAL_ENV)/bin/muffin example
CMD = --help

.PHONY: manage
manage: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -e $(CURDIR)/example
	@$(MANAGER) $(CMD)

.PHONY: run
run: $(VIRTUAL_ENV)/bin/muffin db.sqlite
	@make manage CMD="run --timeout=300 --pid=$(CURDIR)/pid"

.PHONY: daemon
daemon: $(VIRTUAL_ENV)/bin/py.test daemon-kill
	@while nc localhost 5000; do echo 'Waiting for port' && sleep 2; done
	@$(VIRTUAL_ENV)/bin/muffin example run --bind=0.0.0.0:5000 --pid=$(CURDIR)/pid --daemon

.PHONY: daemon-kill
daemon-kill:
	@[ -r $(CURDIR)/pid ] && echo "Kill daemon" `cat $(CURDIR)/pid` && kill `cat $(CURDIR)/pid` || true

.PHONY: watch
watch:
	@make daemon
	@(fswatch -0or $(CURDIR)/example -e "__pycache__" | xargs -0n1 -I {} make daemon) || make daemon-kill

.PHONY: shell
shell: $(VIRTUAL_ENV)
	@make manage CMD=shell

.PHONY: db
db: db.sqlite

db.sqlite: $(VIRTUAL_ENV)
	@make manage CMD=migrate
	@make manage CMD=example_data
