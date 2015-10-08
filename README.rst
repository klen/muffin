.. image:: https://raw.github.com/klen/muffin/develop/logo.png
   :height: 100px
   :width: 100px


The Muffin
##########

.. _badges:

.. image:: http://img.shields.io/travis/klen/muffin.svg?style=flat-square
    :target: http://travis-ci.org/klen/muffin
    :alt: Build Status

.. image:: http://img.shields.io/pypi/v/muffin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin

.. image:: http://img.shields.io/pypi/dm/muffin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin

.. _description:

The Muffin -- A web framework based on Asyncio_ stack ``(early beta)``

Muffin is a fast, simple and asyncronous web-framework for Python_ 3.

Example "Hello User" with the Muffin:

.. code-block:: python

    import muffin


    app = muffin.Application('example')


    @app.register('/', '/hello/{name}')
    def hello(request):
        name = request.match_info.get('name', 'anonymous')
        return 'Hello %s!' % name

Save the script as `example.py` and run it: ::

    $ muffin example run

Open http://fuf.me:5000, http://fuf.me:5000/hello/username in your browser. Enjoy!

.. _contents:

.. contents::

.. _plugins:

Plugins
=======

The list of Muffin plugins:

* `Muffin-Admin   <https://github.com/klen/muffin-admin>`_   -- Basic Admin interface
* `Muffin-Babel   <https://github.com/klen/muffin-babel>`_   -- Localization support
* `Muffin-DebugToolbar <https://github.com/klen/muffin-debugtoolbar>`_ -- Debug Toolbar
* `Muffin-Jade    <https://github.com/klen/muffin-jade>`_    -- Jade templates
* `Muffin-Jinja2  <https://github.com/klen/muffin-jinja2>`_  -- Jinja2 templates
* `Muffin-Metrics <https://github.com/klen/muffin-metrics>`_ -- Send metrics to Graphite/Statsd
* `Muffin-Mongo   <https://github.com/klen/muffin-mongo>`_   -- MongoDB (pymongo) support
* `Muffin-OAuth   <https://github.com/klen/muffin-oauth>`_   -- OAuth client
* `Muffin-Peewee  <https://github.com/klen/muffin-peewee>`_  -- Peewee support (SQL, ORM)
* `Muffin-REST    <https://github.com/klen/muffin-rest>`_    -- Helpers for building REST API
* `Muffin-Redis   <https://github.com/klen/muffin-redis>`_   -- Redis support
* `Muffin-Sentry  <https://github.com/klen/muffin-sentry>`_  -- Sentry integration
* `Muffin-Session <https://github.com/klen/muffin-session>`_ -- User session (auth)

.. _requirements:

Requirements
=============

- python >= 3.3

.. _installation:

Benchmarks
==========

You could find some tests here: http://klen.github.io/py-frameworks-bench/

Installation
=============

**The Muffin** should be installed using pip: ::

    pip install muffin

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
        'DEBUG': False

        # Logging options
        'LOG_LEVEL': 'WARNING'
        'LOG_FORMAT': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s'
        'LOG_DATE_FORMAT': '[%Y-%m-%d %H:%M:%S %z]'

        # List of enabled plugins
        'PLUGINS': []

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

    import pytest

    @pytest.mark.async
    def test_async_code():
        from aiohttp import request
        response = yield from request('GET', 'http://google.com')
        text = yield from response.text()
        assert 'html' in text

    def test_app(app):
        """ Get your app in your tests as fixture. """
        assert app.name == 'my app name'
        assert app.cfg.MYOPTION == 'develop'

    def test_view(client):
        """ Make HTTP request to your application. """
        response = client.get('/my-handler')
        assert 'mydata' in response.text


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

If you wish to express your appreciation for the project, you are welcome to send
a postcard to: ::

    Kirill Klenov
    pos. Severny 8-3
    MO, Istra, 143500
    Russia

.. _links:

.. _klen: https://github.com/klen
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _Python: http://python.org
