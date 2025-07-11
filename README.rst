.. image:: https://raw.github.com/klen/muffin/develop/docs/static/logo-h200.png
   :height: 100px

**Muffin** – fast, lightweight, and asynchronous ASGI_ web framework for Python 3.10+.

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

Why Muffin?
-----------

Muffin combines the simplicity of microframeworks with native ASGI_ performance, supporting multiple async libraries (Asyncio_, Trio_, Curio_) out of the box. Its rich plugin ecosystem makes building modern web applications pleasant and efficient.

Key Features
------------

- ASGI_ compatible
- Competitive performance ([Benchmarks](http://klen.github.io/py-frameworks-bench/))
- Supports Asyncio_, Trio_, and Curio_
- Multiple response types: text, HTML, JSON, streams, files, SSE, WebSockets
- First-class plugin system for templating, databases, auth, and more

Installation
------------

Muffin requires **Python 3.10 or newer**. We recommend using the latest stable Python.

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

Plugins
-------

Muffin has a rich ecosystem of plugins:

- [`muffin-jinja2`](https://github.com/klen/muffin-jinja2) – Jinja2 templates (asyncio/trio/curio)
- [`muffin-session`](https://github.com/klen/muffin-session) – Signed cookie-based HTTP sessions
- [`muffin-oauth`](https://github.com/klen/muffin-oauth) – OAuth integration
- [`muffin-sentry`](https://github.com/klen/muffin-sentry) – Sentry error tracking
- [`muffin-peewee`](https://github.com/klen/muffin-peewee-aio) – Peewee ORM integration
- [`muffin-babel`](https://github.com/klen/muffin-babel) – i18n support
- [`muffin-databases`](https://github.com/klen/muffin-databases) – SQL database support
- [`muffin-mongo`](https://github.com/klen/muffin-mongo) – MongoDB integration
- [`muffin-rest`](https://github.com/klen/muffin-rest) – REST API utilities
- [`muffin-redis`](https://github.com/klen/muffin-redis) – Redis integration
- [`muffin-admin`](https://github.com/klen/muffin-admin) – Auto-generated admin UI
- [`muffin-prometheus`](https://github.com/klen/muffin-prometheus) – Prometheus metrics exporter

See each repo for usage and installation instructions.

Benchmarks
----------

Performance comparisons are available at: http://klen.github.io/py-frameworks-bench/

Bug tracker
-----------

Found a bug or have a feature request? Please open an issue at:
https://github.com/klen/muffin/issues

Contributing
------------

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/klen/muffin/blob/develop/CONTRIBUTING.md) for guidelines.

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
