API
===

.. module:: muffin

This section documents all public interfaces of Muffin.

Application
-----------

.. autoclass:: Application
   :members: route, on_startup, on_shutdown, on_error, middleware, run_after_response, import_submodules

Middleware
~~~~~~~~~~

A coroutine middleware receives the app callable and the raw ASGI arguments:

.. code-block:: python

    from muffin import Application, ResponseHTML

    app = Application()

    @app.middleware
    async def simple_md(app, request, receive, send):
        try:
            response = await app(request, receive, send)
            response.headers["x-simple-md"] = "passed"
            return response
        except RuntimeError:
            return ResponseHTML("Middleware Exception")

Anything else passed to ``app.middleware()`` is treated as ASGI middleware and
bound to the lifespan, which is what most third-party ASGI packages expect:

.. code-block:: python

    from sentry_asgi import SentryMiddleware

    app.middleware(SentryMiddleware)

See :doc:`usage` for the request/response details.

Plugins
-------

.. autoclass:: muffin.plugins.BasePlugin
   :members: setup, startup, shutdown, restart, conftest

The plugin contract is described in :doc:`plugins`.

Class-Based Handlers
--------------------

.. autoclass:: Handler

Request
-------

.. autoclass:: Request
   :members:
   :undoc-members:

A request carries the parsed URL, headers, cookies and path parameters:

.. code-block:: python

    @app.route('/hello/{name}')
    async def hello(request):
        return f"{request.method} {request.url.path} {request.path_params['name']}"

The body is read once, with one of the awaitable parsers (``stream``, ``body``,
``text``, ``json``, ``form``, ``data``); :doc:`usage` covers which to use.

Responses
---------

.. autoclass:: Response
   :members: headers, cookies

Basic response example:

.. code-block:: python

    from muffin import Response

    @app.route('/hello')
    async def hello(request):
        return Response('Hello, world!', content_type='text/plain')

Setting headers:

.. code-block:: python

    @app.route('/example')
    async def example(request):
        response = Response('OK')
        response.headers["X-Version"] = "42"
        return response

Setting cookies:

.. code-block:: python

    @app.route('/example')
    async def example(request):
        response = Response('OK')
        response.cookies["session"] = "xyz"
        response.cookies["session"]["path"] = "/"
        return response


ResponseText
~~~~~~~~~~~~

.. autoclass:: ResponseText

.. code-block:: python

    @app.route('/example')
    async def example(request):
        return ResponseText('Hello, world!')


ResponseHTML
~~~~~~~~~~~~

.. autoclass:: ResponseHTML

.. code-block:: python

    @app.route('/example')
    async def example(request):
        return ResponseHTML('<h1>Hello, world!</h1>')

.. note:: Returning a string/bytes will automatically produce an HTML response.


ResponseJSON
~~~~~~~~~~~~

.. autoclass:: ResponseJSON

.. code-block:: python

    @app.route('/example')
    async def example(request):
        return ResponseJSON({'hello': 'world'})

.. note:: Returning dicts, lists, or booleans produces a JSON response.


ResponseRedirect
~~~~~~~~~~~~~~~~

.. autoclass:: ResponseRedirect

.. code-block:: python

    @app.route('/example')
    async def example(request):
        return ResponseRedirect('/login')

Alternatively, raise as an exception:

.. code-block:: python

    @app.route('/example')
    async def example(request):
        if not request.cookies.get('session'):
            raise ResponseRedirect('/login')
        return 'OK'


ResponseError
~~~~~~~~~~~~~

.. autoclass:: ResponseError

Raise HTTP errors:

.. code-block:: python

    @app.route('/example')
    async def example(request):
        data = await request.data()
        if not data:
            raise ResponseError('Invalid request data', 400)
        return 'OK'

Supports `http.HTTPStatus` shortcuts:

.. code-block:: python

    response = ResponseError.BAD_REQUEST('invalid data')
    response = ResponseError.NOT_FOUND()
    response = ResponseError.BAD_GATEWAY()


ResponseStream
~~~~~~~~~~~~~~

.. autoclass:: ResponseStream

.. code-block:: python

    from muffin import ResponseStream

    async def stream_response():
        for i in range(10):
            await sleep(1)
            yield f"chunk {i}"

    @app.route('/stream')
    async def stream(request):
        return ResponseStream(stream_response())


ResponseSSE
~~~~~~~~~~~

.. autoclass:: ResponseSSE

.. code-block:: python

    from muffin import ResponseSSE

    async def sse_response():
        while True:
            await sleep(1)
            yield {"event": "ping", "data": "pong"}

    @app.route('/sse')
    async def sse(request):
        return ResponseSSE(sse_response())


ResponseFile
~~~~~~~~~~~~

.. autoclass:: ResponseFile

.. code-block:: python

    @app.route('/download')
    async def download(request):
        return ResponseFile('/path/to/file.txt', filename='file.txt')


ResponseWebSocket
~~~~~~~~~~~~~~~~~

.. autoclass:: ResponseWebSocket

.. code-block:: python

    @app.route('/ws')
    async def websocket(request):
        async with ResponseWebSocket(request) as ws:
            msg = await ws.receive()
            await ws.send(f"Echo: {msg}")

Test Client
-----------

.. autoclass:: TestClient

Use for testing your Muffin applications efficiently.

.. Links

.. _ASGI: https://asgi.readthedocs.io/en/latest/
