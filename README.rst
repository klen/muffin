.. image:: https://raw.github.com/klen/muffin/develop/docs/static/logo-h200.png
   :height: 100px

.. _description:

**Muffin** -- is a fast, lightweight and asyncronous ASGI_ web-framework for Python_ 3.

.. _badges:

.. image:: https://github.com/klen/muffin/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin/actions
    :alt: Tests Status

.. image:: https://github.com/klen/muffin/workflows/docs/badge.svg
    :target: https://klen.github.io/muffin
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/muffin
    :target: https://pypi.org/project/muffin/
    :alt: PYPI Version

.. image:: https://img.shields.io/pypi/pyversions/muffin
    :target: https://pypi.org/project/muffin/
    :alt: Python Versions

----------

.. _features:

Features
--------

- ASGI_ compatible;
- `Competitive Performance <http://klen.github.io/py-frameworks-bench/>`_;
- All async python libraries are supported (Asyncio_, Trio_, Curio_);
- Send HTTP (text, html, json, stream, file, http errors) responses
- Support WebSockets, Server Side Events

.. _documentation:

**Docs are available at https://klen.github.io/muffin/. Pull requests
with documentation enhancements and/or fixes are awesome and most welcome.**

.. _contents:

.. contents::

.. _requirements:

.. _installation:

Installation
------------

We recommend using the latest version of Python. The library supports Python
3.7 and newer (PyPy-3.7 are supported too).

Muffin should be installed using pip: ::

    pip install muffin

The command will install minimal configuration.

To install Muffin with `gunicorn`, `uvicorn`, `uvloop`, `httptools` use the
command:

.. code-block:: console

  $ pip install muffin[standard]

Dependencies
````````````

These distributions will be installed automatically when installing **Muffin**.

* `ASGI-Tools`_ - ASGI_ Toolkit
* `Modconfig`_  - Simple hierarchic configuration manager

.. _ASGI-Tools: https://klen.github.io/asgi-tools/
.. _Modconfig: https://pypi.org/project/modconfig/

.. _quickstart:

Quickstart
----------

Example "Hello User" with the Muffin:

.. code-block:: python

    import muffin


    app = muffin.Application()


    @app.route('/', '/hello/{name}')
    async def hello(request):
        name = request.path_params.get('name', 'world')
        return f'Hello {name.title()}!'


What did that code do?

1. First we imported the ``muffin.Application`` class.  An instance of
   this class will be our application.
2. Next we create an instance of this class.
3. We then use the ``muffin.Application.route`` decorator to tell Muffin
   what URLs should trigger our handler function.
4. The function returns the message we want to display in the user's browser.


Save the script as `example.py` and run it using Uvicorn (or another ASGI_ server): ::

    $ uvicorn example:app

Open http://localhost:8000, http://localhost:8000/hello/username in your browser. Enjoy!

.. TODO: Finish the general example
.. For a more complete example, see https://github.com/klen/muffin-example

.. _plugins:

Plugins overview
----------------

The list of some Muffin plugins (please make PR if you want to provide more):

`Muffin-Jinja2  <https://github.com/klen/muffin-jinja2>`_ 
``````````````````````````````````````````````````````````

`Jinja2 <https://jinja.palletsprojects.com/en/2.11.x/>`_ templates (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-jinja2/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-jinja2/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-jinja2
    :target: https://pypi.org/project/muffin-jinja2/
    :alt: PYPI Version



`Muffin-Session <https://github.com/klen/muffin-session>`_ 
```````````````````````````````````````````````````````````

Signed Cookie-Based HTTP sessions (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-session/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-session/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-session
    :target: https://pypi.org/project/muffin-session/
    :alt: PYPI Version


`Muffin-OAuth <https://github.com/klen/muffin-oauth>`_ 
```````````````````````````````````````````````````````

Work with OAuth (authorization, resources loading) (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-oauth/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-oauth/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-oauth
    :target: https://pypi.org/project/muffin-oauth/
    :alt: PYPI Version


`Muffin-Sentry  <https://github.com/klen/muffin-sentry>`_
`````````````````````````````````````````````````````````

Sentry integration (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-sentry/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-sentry/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-sentry
    :target: https://pypi.org/project/muffin-sentry/
    :alt: PYPI Version


`Muffin-Peewee  <https://github.com/klen/muffin-peewee>`_ 
``````````````````````````````````````````````````````````

Peewee support (SQL, ORM) (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-peewee/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-peewee/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-peewee
    :target: https://pypi.org/project/muffin-peewee/
    :alt: PYPI Version


`Muffin-Babel   <https://github.com/klen/muffin-babel>`_
````````````````````````````````````````````````````````

Localization support (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-babel/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-babel/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-babel
    :target: https://pypi.org/project/muffin-babel/
    :alt: PYPI Version


`Muffin-Databases   <https://github.com/klen/muffin-databases>`_
`````````````````````````````````````````````````````````````````

Work with SQL databases (asyncio only)

.. image:: https://github.com/klen/muffin-databases/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-databases/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-databases
    :target: https://pypi.org/project/muffin-databases/
    :alt: PYPI Version


`Muffin-Mongo   <https://github.com/klen/muffin-mongo>`_
`````````````````````````````````````````````````````````

Work with Mongo DB (asyncio only)

.. image:: https://github.com/klen/muffin-mongo/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-mongo/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-mongo
    :target: https://pypi.org/project/muffin-mongo/
    :alt: PYPI Version

`Muffin-REST    <https://github.com/klen/muffin-rest>`_ 
````````````````````````````````````````````````````````

The package provides enhanced support for writing REST APIs (asyncio/trio/curio)

.. image:: https://github.com/klen/muffin-rest/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-rest/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-rest
    :target: https://pypi.org/project/muffin-rest/
    :alt: PYPI Version

`Muffin-Redis   <https://github.com/klen/muffin-redis>`_
`````````````````````````````````````````````````````````

Redis support

.. image:: https://github.com/klen/muffin-redis/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-redis/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-redis
    :target: https://pypi.org/project/muffin-redis/
    :alt: PYPI Version

`Muffin-Admin   <https://github.com/klen/muffin-admin>`_
`````````````````````````````````````````````````````````

Automatically build Admin UI

.. image:: https://github.com/klen/muffin-admin/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-admin/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-admin
    :target: https://pypi.org/project/muffin-admin/
    :alt: PYPI Version

`Muffin-Prometheus   <https://github.com/klen/muffin-prometheus>`_
```````````````````````````````````````````````````````````````````

Prometheus metrics exporter

.. image:: https://github.com/klen/muffin-prometheus/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-prometheus/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-prometheus
    :target: https://pypi.org/project/muffin-prometheus/
    :alt: PYPI Version

.. _benchmarks:

Benchmarks
-----------

You could find some tests here: http://klen.github.io/py-frameworks-bench/

.. _bugtracker:

Bug tracker
-----------

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/muffin/issues

.. _contributing:

Contributing
------------

Development of The Muffin happens at: https://github.com/klen/muffin


Contributors
-------------

Muffin > 0.40 (completelly rewriten from scratch)

* `Kirill Klenov <https://github.com/klen>`_

Muffin < 0.40 (based on AIOHTTP_)

* `Kirill Klenov <https://github.com/klen>`_
* `Andrew Grigorev <https://github.com/ei-grad>`_
* `Diego Garcia <https://github.com/drgarcia1986>`_

.. _license:

License
--------

Licensed under a MIT license (See LICENSE)

.. _links:

.. _AIOHTTP: https://docs.aiohttp.org/en/stable/
.. _ASGI: https://asgi.readthedocs.io/en/latest/
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _Curio: https://curio.readthedocs.io/en/latest/
.. _Python: http://python.org
.. _Trio: https://trio.readthedocs.io/en/stable/index.html
.. _klen: https://github.com/klen
