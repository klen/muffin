# Muffin

<img src="https://raw.githubusercontent.com/klen/muffin/develop/docs/static/logo-h200.png" height="100" alt="Muffin">

Fast, lightweight, asynchronous [ASGI](https://asgi.readthedocs.io/en/latest/) web framework for
Python 3.11+. Documentation: https://klen.github.io/muffin

[![Tests](https://github.com/klen/muffin/workflows/tests/badge.svg)](https://github.com/klen/muffin/actions)
[![Docs](https://github.com/klen/muffin/workflows/docs/badge.svg)](https://klen.github.io/muffin)
[![PyPI](https://img.shields.io/pypi/v/muffin)](https://pypi.org/project/muffin/)
[![Python versions](https://img.shields.io/pypi/pyversions/muffin)](https://pypi.org/project/muffin/)

<!-- description -->
## Why Muffin?

Muffin combines the simplicity of microframeworks with native ASGI performance, supporting
multiple async libraries ([Asyncio](https://docs.python.org/3/library/asyncio.html),
[Trio](https://trio.readthedocs.io/en/stable/index.html),
[Curio](https://curio.readthedocs.io/en/latest/)) out of the box. Its plugin ecosystem covers
templating, databases, auth and more.

Key features:

- ASGI compatible
- [Competitive performance](http://klen.github.io/py-frameworks-bench/)
- Supports Asyncio, Trio and Curio
- Multiple response types: text, HTML, JSON, streams, files, SSE, WebSockets
- First-class plugin system

## Installation

Muffin requires **Python 3.11 or newer**. We recommend using the latest stable Python.

```console
$ pip install muffin
```

For the standard installation with `gunicorn`, `uvicorn`, `uvloop` and `httptools`:

```console
$ pip install muffin[standard]
```

Dependencies installed automatically:

- [ASGI-Tools](https://klen.github.io/asgi-tools/): ASGI toolkit
- [Modconfig](https://pypi.org/project/modconfig/): hierarchical configuration manager

## Quickstart

Create a simple "Hello User" app:

```python
import muffin

app = muffin.Application()


@app.route("/", "/hello/{name}")
async def hello(request):
    name = request.path_params.get("name", "world")
    return f"Hello, {name.title()}!"
```

Save this as `example.py` and run:

```console
$ uvicorn example:app
```

Visit http://localhost:8000 or http://localhost:8000/hello/username in your browser.

<!-- plugins -->
## Plugins

- [muffin-jinja2](https://github.com/klen/muffin-jinja2): Jinja2 templates (asyncio/trio/curio)
- [muffin-session](https://github.com/klen/muffin-session): signed cookie-based HTTP sessions
- [muffin-oauth](https://github.com/klen/muffin-oauth): OAuth1/OAuth2 integration
- [muffin-sentry](https://github.com/klen/muffin-sentry): Sentry error tracking
- [muffin-peewee-aio](https://github.com/klen/muffin-peewee-aio): Peewee ORM integration with async support
- [muffin-babel](https://github.com/klen/muffin-babel): localization with Babel
- [muffin-databases](https://github.com/klen/muffin-databases): async support for a range of databases
- [muffin-mongo](https://github.com/klen/muffin-mongo): MongoDB integration
- [muffin-redis](https://github.com/klen/muffin-redis): Redis integration
- [muffin-rest](https://github.com/klen/muffin-rest): REST helpers
- [muffin-apiclient](https://github.com/klen/muffin-apiclient): support for external APIs
- [muffin-grpc](https://github.com/klen/muffin-grpc): gRPC support
- [muffin-kafka](https://github.com/klen/muffin-kafka): Kafka integration
- [muffin-admin](https://github.com/klen/muffin-admin): admin interface
- [muffin-prometheus](https://github.com/klen/muffin-prometheus): Prometheus metrics exporter

See each repo for usage and installation instructions.

<!-- benchmarks -->
## Benchmarks

Performance comparisons are available at http://klen.github.io/py-frameworks-bench/.

<!-- links -->
## Bug tracker

Found a bug or have a feature request? Please open an issue at
https://github.com/klen/muffin/issues.

## License

Muffin is licensed under the MIT license.

## Credits

**Muffin > 0.40** (completely rewritten on ASGI)

- [Kirill Klenov](https://github.com/klen)

**Muffin < 0.40** (based on [AIOHTTP](https://docs.aiohttp.org/en/stable/))

- [Kirill Klenov](https://github.com/klen)
- [Andrew Grigorev](https://github.com/ei-grad)
- [Diego Garcia](https://github.com/drgarcia1986)
