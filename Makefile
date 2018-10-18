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
	@$(VIRTUAL_ENV)/bin/twine upload dist/*.tar.gz || true
	@$(VIRTUAL_ENV)/bin/twine upload dist/*.whl || true
	@$(VIRTUAL_ENV)/bin/pip install -e $(CURDIR)

# =============
#  Development
# =============

$(VIRTUAL_ENV): requirements.txt
	@[ -d $(VIRTUAL_ENV) ] || virtualenv --python=python3 $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

.PHONY: test
# target: test - Run tests
test: $(VIRTUAL_ENV)/bin/py.test
	@$(VIRTUAL_ENV)/bin/py.test tests

.PHONY: t
t: test

.PHONY: tp
tp:
	@echo 'Test Muffin-Jinja2'
	make -C $(CURDIR)/plugins/muffin-jinja2 t
	@echo 'Test Muffin-Peewee'
	make -C $(CURDIR)/plugins/muffin-peewee t
	@echo 'Test Muffin-Session'
	make -C $(CURDIR)/plugins/muffin-session t
	@echo 'Test Muffin-Admin'
	make -C $(CURDIR)/plugins/muffin-admin t
	@echo 'Test Muffin-OAuth'
	make -C $(CURDIR)/plugins/muffin-oauth t
	@echo 'Test Muffin-REST'
	make -C $(CURDIR)/plugins/muffin-rest t
	@echo 'Test Muffin-Redis'
	make -C $(CURDIR)/plugins/muffin-redis t
	# @echo 'Test Muffin-DebugToolbar'
	# make -C $(CURDIR)/plugins/muffin-debugtoolbar t
	# @echo 'Test Muffin-Jade'
	# make -C $(CURDIR)/plugins/muffin-jade t
	# @echo 'Test Muffin-Metrics'
	# make -C $(CURDIR)/plugins/muffin-metrics t
	# @echo 'Test Muffin-Mongo'
	# make -C $(CURDIR)/plugins/muffin-mongo t
	# @echo 'Test Muffin-Sentry'
	# make -C $(CURDIR)/plugins/muffin-sentry t

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
