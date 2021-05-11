API
===

.. module:: muffin

This part of the documentation covers the interfaces of Muffin

Application
-----------

.. autoclass:: Application

   .. automethod:: route

   .. automethod:: on_startup

   .. automethod:: on_shutdown

   .. automethod:: on_error

   .. automethod:: middleware


Class Based Handlers
--------------------

.. autoclass:: Handler

Request
-------

.. autoclass:: Request

    The Request object contains all the information about an incoming HTTP
    request.

    .. code-block:: python

        @app.route('/')
        async def home(request):
            response = f"{ request.method } { request.url.path }"
            return response

    Requests are based on a given ASGI_ scope and represents a mapping interface.

    .. code-block:: python

        request = Request(scope)
        assert request['version'] == scope['version']
        assert request['method'] == scope['method']
        assert request['scheme'] == scope['scheme']
        assert request['path'] == scope['path']

        # and etc

        # ASGI Scope keys also are available as Request attrubutes.

        assert request.version == scope['version']
        assert request.method == scope['method']
        assert request.scheme == scope['scheme']

    .. autoattribute:: query

    .. autoattribute:: headers

    .. autoattribute:: cookies

    .. autoattribute:: charset

    .. autoattribute:: content_type

    .. autoattribute:: url

    .. automethod:: stream

        .. code-block:: python

            @app.route('/repeater')
            async def repeater(request):
                body = b''
                async for chunk in request.stream():
                    body += chunk

                return body

    .. automethod:: body

    .. automethod:: text

    .. automethod:: form

    .. automethod:: json

    .. automethod:: data

Responses
---------

.. autoclass:: Response

    A helper to make http responses.

    .. code-block:: python

        from muffin import Response

        @app.route('/hello')
        async def hello(request):
            response = Response('Hello, world!', content_type='text/plain')
            return response

    .. autoattribute:: headers

        .. code-block:: python

            from muffin import Response

            @app.route('/example')
            async def example(request):
                response = Response('OK')
                response.headers["X-Version"] = "42"
                return response

    .. autoattribute:: cookies

        .. code-block:: python

            from muffin import Response

            @app.route('/example')
            async def example(request):
                response = Response('OK')
                response.cookies["rocky"] = "road"
                response.cookies["rocky"]["path"] = "/cookie"
                return response



ResponseText (:class:`Response`)
````````````````````````````````

.. autoclass:: ResponseText

    .. code-block:: python

        from muffin import ResponseText

        @app.route('/example')
        async def example(request):
            return ResponseText('Hello, world!')


ResponseHTML (:class:`Response`)
````````````````````````````````

.. autoclass:: ResponseHTML

    .. code-block:: python

        from muffin import ResponseHTML

        @app.route('/example')
        async def example(request):
            return ResponseHTML('<h1>Hello, world!</h1>')

    .. note:: If your view function returns a string/byte-string the
                result will be converted into a HTML Response


ResponseJSON (:class:`Response`)
````````````````````````````````

.. autoclass:: ResponseJSON

    .. code-block:: python

        from muffin import ResponseJSON

        @app.route('/example')
        async def example(request):
            return ResponseJSON({'hello': 'world'})

    .. note:: If your view function returns a dictionary/list/boolean the
                result will be converted into a JSON Response


ResponseRedirect (:class:`Response`)
````````````````````````````````````

.. autoclass:: ResponseRedirect

    .. code-block:: python

        from muffin import ResponseRedirect

        @app.route('/example')
        async def example(request):
            return ResponseRedirect('/login')

    You are able to raise the :py:class:`ResponseRedirect` as an exception.

    .. code-block:: python

        from muffin import ResponseRedirect

        @app.route('/example')
        async def example(request):
            if not request.headers.get('authorization'):
                # The client will be redirected to "/login"
                raise ResponseRedirect('/login')

            return 'OK'


ResponseError (:class:`Response`)
`````````````````````````````````

.. py:class:: ResponseError(message=None, status_code=500, **kwargs)

    A helper to return HTTP errors. Uses a 500 status code by default.

    .. :comment: ***

    :param message: A string with the error's message (HTTPStatus messages will be used by default)

    .. code-block:: python

        from muffin import ResponseError

        @app.route('/example')
        async def example(request):
            return ResponseError('Timeout', 502)

    You are able to raise the :py:class:`ResponseError` as an exception.

    .. code-block:: python

        from muffin import ResponseError

        @app.route('/example')
        async def example(request):
            data = await request.data()
            if not data:
                raise ResponseError('Invalid request data', 400)

            return 'OK'

    You able to use :py:class:`http.HTTPStatus` properties with the `ResponseError` class

    .. code-block:: python

        response = ResponseError.BAD_REQUEST('invalid data')
        response = ResponseError.NOT_FOUND()
        response = ResponseError.BAD_GATEWAY()
        # and etc


ResponseStream (:class:`Response`)
``````````````````````````````````

.. autoclass:: ResponseStream

    .. code-block:: python

        from muffin import ResponseStream

        async def stream_response():
            for number in range(10):
                await sleep(1)
                yield str(number)

        @app.route('/example')
        async def example(request):
            generator = stream_response()
            return ResponseStream(generator, content_type='plain/text')


ResponseSSE (:class:`Response`)
```````````````````````````````

.. autoclass:: ResponseSSE

    .. code-block:: python

        from muffin import ResponseSSE

        async def stream_response():
            for number in range(10):
                await aio_sleep(1)
                # The response support messages as text
                yield "data: message text"

                # And as dictionaties as weel
                yield {
                    "event": "ping",
                    "data": time.time(),
                }

        @app.route('/example')
        async def example(request):
            generator = stream_response()
            return ResponseSSE(generator, content_type='plain/text')


ResponseFile (:class:`Response`)
````````````````````````````````

.. autoclass:: ResponseFile

    .. code-block:: python

        from muffin import ResponseFile

        @app.route('/example')
        async def example(request):
            return ResponseFile('/storage/my_best_selfie.jpeg')


ResponseWebSocket (:class:`Response`)
`````````````````````````````````````

.. autoclass:: ResponseWebSocket

    .. code-block:: python

        from muffin import ResponseWebsocket

        @app.route('/example')
        async def example(request):
            async with ResponseWebSocket(request) as ws:
                msg = await ws.receive()
                assert msg == 'ping'
                await ws.send('pong')

    .. automethod:: accept

    .. automethod:: close

    .. automethod:: send

    .. automethod:: send_json

    .. automethod:: receive

Test Client
-----------

.. autoclass:: TestClient

.. Links

.. _ASGI: https://asgi.readthedocs.io/en/latest/
