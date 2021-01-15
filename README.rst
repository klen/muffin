.. image:: https://raw.github.com/klen/muffin/develop/docs/static/logo.png
   :height: 100px
   :width: 100px


The Muffin
##########

.. _badges:

.. image:: https://github.com/klen/muffin/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin
    :target: https://pypi.org/project/muffin/
    :alt: PYPI Version

.. _important:

    The framework has been created in 2015 when asyncio/aiohttp stack was very
    young and small. It was an attempt to build a foundation for asyncio web
    based project with all required tools (plugins system, admin interfaces,
    REST API and etc). For current moment (2018) aiohttp stack is quite good
    and the Muffin is depricated. It can be supported because some projects
    still use it but if you are planning to start a new project I would
    recomend to have a look on something else.

.. _description:

    **Muffin** -- A web framework based on Asyncio_ stack ``(depricated)``
    Muffin is a fast, simple and asyncronous web-framework for Python_ 3.

.. _documentation:

**Docs are available at https://muffin.readthedocs.org/. Pull requests
with documentation enhancements and/or fixes are awesome and most welcome.**

Example "Hello User" with the Muffin:

.. code-block:: python

    import muffin


    app = muffin.Application('example')


    @app.route('/', '/hello/{name}')
    async def hello(request):
        name = request.path_params.get('name', 'anonymous')
        return f'Hello {name.title()}!'


Save the script as `example.py` and run it using Uvicorn (or another ASGI server): ::

    $ uvicorn example:app

Open http://localhost:5000, http://localhost:5000/hello/username in your browser. Enjoy!

For a more complete example, see https://github.com/klen/muffin-example

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.8

.. _installation:

Installation
=============

**The Muffin** should be installed using pip: ::

    pip install muffin

.. _plugins:

Plugins
========

The list of some Muffin plugins (please make PR if you want to provide more):

* `Muffin-Jinja2  <https://github.com/klen/muffin-jinja2>`_  -- Jinja2 templates

.. image:: https://github.com/klen/muffin-jinja2/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-jinja2/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-jinja2
    :target: https://pypi.org/project/muffin-jinja2/
    :alt: PYPI Version

* `Muffin-Admin   <https://github.com/klen/muffin-admin>`_   -- Basic Admin interface

  .. image:: http://img.shields.io/travis/klen/muffin-admin.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-admin

  .. image:: http://img.shields.io/pypi/v/muffin-admin.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-admin

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-admin.svg?style=flat-square
     :target: https://github.com/klen/muffin-admin/issues

* `Muffin-Babel   <https://github.com/klen/muffin-babel>`_   -- Localization support

  .. image:: http://img.shields.io/travis/klen/muffin-babel.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-babel

  .. image:: http://img.shields.io/pypi/v/muffin-babel.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-babel

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-babel.svg?style=flat-square
     :target: https://github.com/klen/muffin-babel/issues

* `Muffin-DebugToolbar <https://github.com/klen/muffin-debugtoolbar>`_ -- Debug Toolbar

  .. image:: http://img.shields.io/travis/klen/muffin-debugtoolbar.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-debugtoolbar

  .. image:: http://img.shields.io/pypi/v/muffin-debugtoolbar.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-debugtoolbar

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-debugtoolbar.svg?style=flat-square
     :target: https://github.com/klen/muffin-debugtoolbar/issues

* `Muffin-Jade    <https://github.com/klen/muffin-jade>`_    -- Jade templates

  .. image:: http://img.shields.io/travis/klen/muffin-jade.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-jade

  .. image:: http://img.shields.io/pypi/v/muffin-jade.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-jade

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-jade.svg?style=flat-square
     :target: https://github.com/klen/muffin-jade/issues

* `Muffin-Metrics <https://github.com/klen/muffin-metrics>`_ -- Send metrics to Graphite/Statsd

  .. image:: http://img.shields.io/travis/klen/muffin-metrics.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-metrics

  .. image:: http://img.shields.io/pypi/v/muffin-metrics.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-metrics

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-metrics.svg?style=flat-square
     :target: https://github.com/klen/muffin-metrics/issues

* `Muffin-Mongo   <https://github.com/klen/muffin-mongo>`_   -- MongoDB (pymongo) support

  .. image:: http://img.shields.io/travis/klen/muffin-mongo.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-mongo

  .. image:: http://img.shields.io/pypi/v/muffin-mongo.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-mongo

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-mongo.svg?style=flat-square
     :target: https://github.com/klen/muffin-mongo/issues

* `Muffin-Motor   <https://github.com/drgarcia1986/muffin-motor>`_   -- MongoDB (motor) support

  .. image:: http://img.shields.io/travis/drgarcia1986/muffin-motor.svg?style=flat-square
     :target: http://travis-ci.org/drgarcia1986/muffin-motor

  .. image:: http://img.shields.io/pypi/v/muffin-motor.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-motor

  .. image:: https://img.shields.io/github/issues-raw/drgarcia1986/muffin-motor.svg?style=flat-square
     :target: https://github.com/drgarcia1986/muffin-motor/issues

* `Muffin-OAuth   <https://github.com/klen/muffin-oauth>`_   -- OAuth client

  .. image:: http://img.shields.io/travis/klen/muffin-oauth.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-oauth

  .. image:: http://img.shields.io/pypi/v/muffin-oauth.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-oauth

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-oauth.svg?style=flat-square
     :target: https://github.com/klen/muffin-oauth/issues

* `Muffin-Peewee  <https://github.com/klen/muffin-peewee>`_  -- Peewee support (SQL, ORM)

  .. image:: http://img.shields.io/travis/klen/muffin-peewee.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-peewee

  .. image:: http://img.shields.io/pypi/v/muffin-peewee.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-peewee

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-peewee.svg?style=flat-square
     :target: https://github.com/klen/muffin-peewee/issues

* `Muffin-REST    <https://github.com/klen/muffin-rest>`_    -- Helpers for building REST API

  .. image:: http://img.shields.io/travis/klen/muffin-rest.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-rest

  .. image:: http://img.shields.io/pypi/v/muffin-rest.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-rest

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-rest.svg?style=flat-square
     :target: https://github.com/klen/muffin-rest/issues

* `Muffin-Redis   <https://github.com/klen/muffin-redis>`_   -- Redis support

  .. image:: http://img.shields.io/travis/klen/muffin-redis.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-redis

  .. image:: http://img.shields.io/pypi/v/muffin-redis.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-redis

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-redis.svg?style=flat-square
     :target: https://github.com/klen/muffin-redis/issues

* `Muffin-Sentry  <https://github.com/klen/muffin-sentry>`_  -- Sentry integration

  .. image:: http://img.shields.io/travis/klen/muffin-sentry.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-sentry

  .. image:: http://img.shields.io/pypi/v/muffin-sentry.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-sentry

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-sentry.svg?style=flat-square
     :target: https://github.com/klen/muffin-sentry/issues

* `Muffin-Session <https://github.com/klen/muffin-session>`_ -- User session (auth)

  .. image:: http://img.shields.io/travis/klen/muffin-session.svg?style=flat-square
     :target: http://travis-ci.org/klen/muffin-session

  .. image:: http://img.shields.io/pypi/v/muffin-session.svg?style=flat-square
     :target: https://pypi.python.org/pypi/muffin-session

  .. image:: https://img.shields.io/github/issues-raw/klen/muffin-session.svg?style=flat-square
     :target: https://github.com/klen/muffin-session/issues

.. _benchmarks:

Benchmarks
==========

You could find some tests here: http://klen.github.io/py-frameworks-bench/

.. _usage:

Usage
=====

See more in the example application sources. The application is deployed on Heroku:
https://muffin-py.herokuapp.com

Run example server locally: ::

    $ make -C example run

And open http://fuf.me:5000 in your browser.

Configuration
-------------

Muffin gets configuration options from python files. You have to specify
default configuration module name in your app initialization:

.. code-block:: python

  app = muffin.Application('myapp', CONFIG='config.debug')

This name could be overriden by ``MUFFIN_CONFIG`` environment variable: ::

  $ MUFFIN_CONFIG=settings_local muffin example run

Which in its turn could be overriden by ``--config`` param of ``muffin`` command: ::

  $ muffin --config=config.debug example run

Also you can define default config parameter values while initializing your application:

.. code-block:: python

  app = muffin.Application('myapp', DEBUG=True, ANY_OPTION='Here', ONE_MORE='Yes')

Base application options
^^^^^^^^^^^^^^^^^^^^^^^^

Base Muffin options and default values:

.. code-block:: python

        # Configuration module
        'CONFIG': 'config'

        # Enable debug mode
        'DEBUG': ...

        # Logging options
        'ACCESS_LOG': '-',  # File path to access log, - to stderr
        'ACCESS_LOG_FORMAT': '%a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i"',
        'LOG_LEVEL': 'WARNING'
        'LOG_FORMAT': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s'
        'LOG_DATE_FORMAT': '[%Y-%m-%d %H:%M:%S %z]'

        # Setup static files in development
        'STATIC_PREFIX': '/static'
        'STATIC_FOLDERS': ['static']


Configuring logging
^^^^^^^^^^^^^^^^^^^
You can define your logging configurations with `Python dictConfig format  <https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema>`_ and place in ``LOGGING`` conf:

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
            },
        },
        'handlers': {
            'logfile': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'my_log.log',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 10
            },
        },
        'loggers': {
            '': {
                'handlers': ['logfile'],
                'level': 'ERROR'
            },
            'project': {
                'level': 'INFO',
                'propagate': True,
            },
        }
    }

To use just get logger with ``logging.getLogger()``:

.. code-block:: python

    import logging
    logger = logging.getLogger('project')

CLI integration
---------------

Run in your shell: ::

    $ muffin path.to.your.module:app_object_name --help

Write a custom command
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @app.manage.command
    def hello(name, upper=False):
        """ Write command help text here.

        :param name:  Write your name
        :param upper: Use uppercase

        """
        greetings = 'Hello %s!' % name
        if upper:
            greetings = greetings.upper()
        print(greetings)

::

    $ muffin example hello --help

        Write command help text here.

        positional arguments:
        name        Write your name

        optional arguments:
        -h, --help  show this help message and exit
        --upper     Enable use uppercase
        --no-upper  Disable use uppercase

    $ muffin example hello mike --upper

        HELLO MIKE!

.. _testing:

Testing
========

Setup tests
-----------

Set module path to your Muffin Application in pytest configuration file or use
command line option ``--muffin-app``.

Example: ::

    $ py.test -xs --muffin-app example

Testing application
-------------------

See examples:

.. code-block:: python

    async def test_async_code():
        async def coro():
            return True

        assert await coro()

    def test_app(app):
        """ Get your app in your tests as fixture. """
        assert app.name == 'my app name'
        assert app.cfg.MYOPTION == 'develop'

    async def test_view(client):
        """ Make HTTP request to your application. """
        async with client.get('/my-handler') as resp:
            text = await resp.text()
            assert 'mydata' in text

Also please check `aiohttp testing documentation <https://docs.aiohttp.org/en/stable/testing.html>`_.


.. _deployment:

Deployment
==========

Use ``muffin`` command. By example: ::

    $ muffin example run --workers=4

See ``muffin {APP} run --help`` for more info.

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/muffin/issues

.. _contributing:

Contributing
============

Development of The Muffin happens at: https://github.com/klen/muffin


Contributors
=============

* `Andrew Grigorev <https://github.com/ei-grad>`_
* `Diego Garcia <https://github.com/drgarcia1986>`_
* `Kirill Klenov <https://github.com/klen>`_

.. _license:

License
========

Licensed under a MIT license (See LICENSE)

.. _links:

.. _klen: https://github.com/klen
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _Python: http://python.org
