Errors
======

Responses as exceptions
-----------------------

:class:`~muffin.ResponseRedirect` and :class:`~muffin.ResponseError` are
responses, and raising one is the normal way to stop a handler:

.. code-block:: python

    from muffin import ResponseError, ResponseRedirect

    @app.route("/private")
    async def private(request):
        if not request.cookies.get("auth"):
            raise ResponseError.UNAUTHORIZED()
        raise ResponseRedirect("/login")

Every HTTP status has a shortcut on ``ResponseError``: ``BAD_REQUEST()``,
``NOT_FOUND()``, ``METHOD_NOT_ALLOWED()``, ``INTERNAL_SERVER_ERROR()``,
``BAD_GATEWAY()`` and so on. They accept an optional message and headers:

.. code-block:: python

    raise ResponseError.NOT_FOUND("No such page", headers={"Cache-Control": "no-store"})

The router raises these too: an unknown path is ``ResponseError.NOT_FOUND`` and a
matching path with the wrong method is ``ResponseError.METHOD_NOT_ALLOWED``, so
custom handlers for them cover routing as well.

Exception handlers
------------------

``app.on_error(SomeException)`` registers a handler. It receives the request and
the exception, and whatever it returns is converted to a response like any other
return value:

.. code-block:: python

    @app.on_error(ResponseError)
    async def on_response_error(request, error):
        if error.status_code == 404:
            return ResponseError.NOT_FOUND("Custom 404 Page")
        return error

.. code-block:: python

    @app.on_error(ValueError)
    async def on_value_error(request, error):
        app.logger.warning("Bad input: %s", error)
        return 400, {"error": "bad input"}

Handlers are looked up along the exception's MRO, so the first matching class
wins: register ``ValidationError`` for the specific case and ``Exception`` for
everything else. Order of registration does not matter, the exception type does.

Unhandled exceptions
--------------------

Without a matching handler, Muffin logs the traceback and returns a plain 500
response; the connection stays usable:

.. code-block:: python

    @app.route("/boom")
    async def boom(request):
        raise RuntimeError("unexpected")     # logged, 500, no traceback to the client

With ``DEBUG=True`` the exception is not caught at all: it propagates to the ASGI
server, which prints the traceback and closes the response. That is what you want
in development and never in production.

Muffin's own exceptions
-----------------------

.. autoclass:: muffin.errors.MuffinError

.. autoclass:: muffin.errors.AsyncRequiredError
   :members: __init__

.. autoclass:: muffin.errors.InvalidAppError
   :members: __init__

Plugin errors (``PluginError``, ``PluginNotInstalledError``) are documented in
:doc:`plugins`.

``AsyncRequiredError`` and ``InvalidAppError`` appear at application definition
time, not at request time: the first when a handler method is not a coroutine, or
when a command registered with ``lifespan=True`` is not async; the second when
``import_app`` cannot resolve the given path.

``PluginNotInstalledError`` is raised by the ``plugin.app`` property when a
plugin was created but never bound to an application, including plugins that were
disabled by configuration.

Errors from ASGI middleware
---------------------------

Internal middleware runs inside request processing, so exceptions raised there
are handled by the same exception handlers. ASGI middleware bound to the
lifespan sits outside it; it sees the raw exceptions that escape, and a failing
one can break the connection rather than return a response.
