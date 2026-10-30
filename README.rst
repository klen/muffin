.. image:: https://raw.github.com/klen/muffin/develop/docs/static/logo-h200.png
   :height: 100px

**Muffin** – fast, lightweight, and asynchronous ASGI_ web framework for Python 3.11+.

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

.. _description:

Why Muffin?
-----------

Muffin combines the simplicity of microframeworks with native ASGI_ performance, supporting multiple async libraries (Asyncio_, Trio_, Curio_) out of the box. Its rich plugin ecosystem makes building modern web applications pleasant and efficient.

Key Features
------------

- ASGI_ compatible
- Competitive performance (`Benchmarks <http://klen.github.io/py-frameworks-bench/>`_)
- Supports Asyncio_, Trio_, and Curio_
- Multiple response types: text, HTML, JSON, streams, files, SSE, WebSockets
- First-class plugin system for templating, databases, auth, and more

.. _installation:

Installation
------------

Muffin requires **Python 3.11 or newer**. We recommend using the latest stable Python.

Install via pip:

.. code-block:: console

    $ pip install muffin

For the standard installation with `gunicorn`, `uvicorn`, `uvloop`, `httptools`:

.. code-block:: console

    $ pip install muffin[standard]

Dependencies
~~~~~~~~~~~~

These packages will be installed automatically:

* `ASGI-Tools`_ – ASGI toolkit
* `Modconfig`_  – hierarchical configuration manager

.. _ASGI-Tools: https://klen.github.io/asgi-tools/
.. _Modconfig: https://pypi.org/project/modconfig/

.. _quickstart:

Quickstart
----------

Create a simple "Hello User" app:

.. code-block:: python

    import muffin

    app = muffin.Application()

    @app.route('/', '/hello/{name}')
    async def hello(request):
        name = request.path_params.get('name', 'world')
        return f'Hello, {name.title()}!'

Save this as `example.py` and run:

.. code-block:: console

    $ uvicorn example:app

Visit http://localhost:8000 or http://localhost:8000/hello/username in your browser.

.. _plugins:

Plugins
-------

Muffin has a rich ecosystem of plugins:

- `muffin-jinja2 <https://github.com/klen/muffin-jinja2>`_ -- Jinja2 templates (asyncio/trio/curio)
- `muffin-session <https://github.com/klen/muffin-session>`_ -- Signed cookie-based HTTP sessions
- `muffin-oauth <https://github.com/klen/muffin-oauth>`_ -- OAuth1/OAuth2 integration
- `muffin-sentry <https://github.com/klen/muffin-sentry>`_ -- Sentry error tracking
- `muffin-peewee-aio <https://github.com/klen/muffin-peewee-aio>`_ -- Peewee ORM integration with async support
- `muffin-babel <https://github.com/klen/muffin-babel>`_ -- Localization with Babel
- `muffin-databases <https://github.com/klen/muffin-databases>`_ -- Async support for a range of databases
- `muffin-mongo <https://github.com/klen/muffin-mongo>`_ -- MongoDB integration
- `muffin-redis <https://github.com/klen/muffin-redis>`_ -- Redis integration
- `muffin-rest <https://github.com/klen/muffin-rest>`_ -- REST helpers
- `muffin-apiclient <https://github.com/klen/muffin-apiclient>`_ -- Support for external APIs
- `muffin-grpc <https://github.com/klen/muffin-grpc>`_ -- GRPC support
- `muffin-kafka <https://github.com/klen/muffin-kafka>`_ -- Kafka integration
- `muffin-admin <https://github.com/klen/muffin-admin>`_ -- Admin interface
- `muffin-prometheus <https://github.com/klen/muffin-prometheus>`_ -- Prometheus metrics exporter

See each repo for usage and installation instructions.

.. _benchmarks:

Benchmarks
----------

Performance comparisons are available at: http://klen.github.io/py-frameworks-bench/

.. _links:

Bug tracker
-----------

Found a bug or have a feature request? Please open an issue at:
https://github.com/klen/muffin/issues

License
-------

Muffin is licensed under the MIT license.

----------

Credits
-------

**Muffin > 0.40 (completely rewritten on ASGI)**

* `Kirill Klenov <https://github.com/klen>`_

**Muffin < 0.40 (based on AIOHTTP_)**

* `Kirill Klenov <https://github.com/klen>`_
* `Andrew Grigorev <https://github.com/ei-grad>`_
* `Diego Garcia <https://github.com/drgarcia1986>`_

.. _AIOHTTP: https://docs.aiohttp.org/en/stable/
.. _ASGI: https://asgi.readthedocs.io/en/latest/
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _Curio: https://curio.readthedocs.io/en/latest/
.. _Python: http://python.org
.. _Trio: https://trio.readthedocs.io/en/stable/index.html
.. _MIT license: http://opensource.org/licenses/MIT
