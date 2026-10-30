Testing
=======

Muffin ships a test client and a pytest plugin, so an application can be tested
without a server.

TestClient
----------

:class:`~muffin.TestClient` is the ASGI test client from ``asgi-tools``. It
builds ASGI messages directly and never opens a socket.

Application code:

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.route("/")
    async def home(request):
        return "OK"

Test:

.. code-block:: python

    from muffin import TestClient

    client = TestClient(app)

    response = await client.get("/")
    assert response.status_code == 200
    assert await response.text() == "OK"

The client keeps cookies between requests, so a login flow can be tested in
order. Supported method shortcuts (``get``, ``post``, ``put``, ``patch``,
``delete``, and any other method name) accept the arguments of ``request``:

.. code-block:: python

    response = await client.post(
        "/login",
        data={"username": "admin", "password": "secret"},
    )
    assert response.status_code == 200

    response = await client.get("/search", query={"q": "muffin"})
    assert (await response.json()) == {"found": 1}

Useful arguments: ``query``, ``data`` (bytes, text or a dict; uploaded files make
it multipart), ``json``, ``headers``, ``cookies`` and ``follow_redirect``
(``True`` by default). The response exposes ``status_code``, ``headers``,
``cookies`` and the awaitable ``body()``, ``text()`` and ``json()``.

Lifespan events do not run implicitly. Wrap the calls that need them:

.. code-block:: python

    async with client.lifespan():
        response = await client.get("/health")

WebSocket routes are tested with ``websocket()``:

.. code-block:: python

    from muffin import Application, ResponseWebSocket

    app = Application()

    @app.route("/ws")
    async def socket(request):
        async with ResponseWebSocket(request) as ws:
            msg = await ws.receive()
            if msg == "ping":
                await ws.send("pong")

.. code-block:: python

    client = TestClient(app)

    async with client.websocket("/ws") as ws:
        await ws.send("ping")
        assert await ws.receive() == "pong"

Pytest integration
------------------

The pytest plugin is enabled by the ``muffin.pytest`` entry point, so installing
Muffin is enough. Point pytest at your application with a config entry or the
``--muffin-app`` option:

.. code-block:: ini

    # pyproject.toml or pytest.ini
    muffin_app = "example"

.. code-block:: console

    $ pytest --muffin-app example

A configuration module can be pinned the same way, with ``muffin_config`` or
``--muffin-config``; it sets ``MUFFIN_CONFIG`` before the app is imported.

Available fixtures:

- ``app``: the application, with lifespan started and plugin ``startup`` hooks
  awaited, so plugin clients are ready
- ``client``: a :class:`~muffin.TestClient` bound to ``app``

Async tests need an async runner. Muffin's ``app`` fixture itself depends on the
``aiolib`` fixture, so the suite needs `pytest-aio
<https://github.com/klen/pytest-aio>`_. With it installed, async tests and async
fixtures are wrapped automatically; no markers are needed. Parametrizing
``aiolib`` is how one suite runs on asyncio, trio and curio:

.. code-block:: python

    @pytest.fixture(
        params=["asyncio", "trio", "curio"],
        scope="session",
    )
    def aiolib(request):
        return request.param

Per-test applications
---------------------

The plugin's ``app`` fixture is session-scoped, which is fast but leaks state
between tests: a row created in one test is still there in the next. For tests
that write, define a function-scoped fixture in ``conftest.py``; it overrides the
plugin's fixture of the same name:

.. code-block:: python

    import pytest

    from muffin import TestClient


    @pytest.fixture
    def app(monkeypatch):
        monkeypatch.setenv("MUFFIN_DEBUG", "true")     # before the app is imported
        from example import app as example_app
        return example_app


    @pytest.fixture
    def client(app):
        return TestClient(app)

Environment variables must be set before the application is imported, so import
it inside the fixture, not at module import time. To test with a config module,
set ``MUFFIN_CONFIG`` the same way.

Testing error handlers and streams
----------------------------------

Error handlers are tested like routes: they only need a request that fails.
Streams and SSE are read to the end by the client, so one ``await`` is enough:

.. code-block:: python

    async def test_custom_404(client):
        response = await client.get("/nope")
        assert response.status_code == 404
        assert await response.text() == "Custom 404 Page"

    async def test_sse(client):
        response = await client.get("/events")
        assert "text/event-stream" in response.headers["content-type"]
        assert (await response.text()).startswith("event: tick")

.. warning::

   If pytest warns ``cannot collect test class 'ASGITestClient'``, rename the
   import in that module: ``from muffin import TestClient as Client``. The client
   is not a test class, but its name matches pytest's collection pattern.
