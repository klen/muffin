Usage
=====

Quickstart
----------

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.route("/")
    async def hello_world(request):
        return "<p>Hello, World!</p>"

Save it as :file:`hello.py` and run it with an ASGI server:

.. code-block:: bash

    uvicorn hello:app --reload

Open http://127.0.0.1:8000/. The view returns a string, and Muffin sends it as
an HTML response. Application options (name, debug, static files, logging) are
described in :doc:`configuration`.

Request
-------

A view is a coroutine that receives a :class:`~muffin.Request`:

.. code-block:: python

    @app.route("/login", methods=["POST"])
    async def login(request):
        form = await request.form()
        username = form.get("username")
        if username == "admin":
            return f"Welcome, {username}"
        return "Invalid credentials"

Everything the server already parsed is an attribute: ``request.method``,
``request.url``, ``request.query``, ``request.headers``, ``request.cookies`` and
``request.path_params``.

The body is read with an awaitable parser. Pick one: the body is consumed by the
first reader.

- ``await request.body()``: raw bytes
- ``await request.text()``: decoded text
- ``await request.json()``: parsed JSON
- ``await request.form()``: ``multipart/form-data`` or urlencoded form
- ``await request.data()``: JSON, form or text, chosen by ``Content-Type``

.. code-block:: python

    search = request.query.get("search", "")
    session = request.cookies.get("session")

    form = await request.form()
    upload = form["file"]
    content = await upload.read()

Routing
-------

.. code-block:: python

    @app.route("/")
    async def index(request):
        return "Index Page"

    @app.route("/users", "/users/{username}", methods=["GET", "POST"])
    async def user(request):
        return f"Hello, {request.path_params.get('username', 'guest')}"

Pass several paths and ``methods`` to one handler when they share the
implementation. Without ``methods`` the handler accepts every method.
A trailing slash is ignored unless ``TRIM_LAST_SLASH`` is disabled.

Path parameters support type converters:

========= ==============================================
``str``   (default) any text without a slash
``int``   digits, converted to ``int``
``float`` digits with an optional fraction
``path``  like ``str`` but also accepts slashes
``uuid``  UUID string, converted to ``uuid.UUID``
========= ==============================================

.. code-block:: python

    @app.route("/post/{post_id:int}")
    async def post(request):
        post_id = request.path_params["post_id"]
        return f"Post #{post_id}"

Compiled regular expressions work as paths too. The pattern is matched from the
beginning of the path, so anchor it if you need an exact match:

.. code-block:: python

    import re

    @app.route(re.compile(r"^/item/(a|b|c)/$"))
    async def item(request):
        return request.path

Class-based handlers are described in :doc:`api`.

Static Files
------------

Static files are served by the application itself, which is fine for development
and for deployments where a proxy serves them directly; see :doc:`deploy`:

.. code-block:: python

    app = Application(STATIC_FOLDERS=["static"], STATIC_URL_PREFIX="/assets")

``/assets/logo.png`` is now served from ``static/logo.png``. Put static handling
in the options, not in ``__init__`` arguments other than the configuration ones;
see :doc:`configuration`.

Redirects and Errors
--------------------

Both redirects and errors are responses, so they can be returned or raised:

.. code-block:: python

    from muffin import ResponseError, ResponseRedirect

    @app.route("/")
    async def index(request):
        raise ResponseRedirect("/login")

    @app.route("/secure")
    async def secure(request):
        if not request.cookies.get("auth"):
            raise ResponseError.UNAUTHORIZED()
        return "Secret data"

``ResponseError`` gives a constructor for every HTTP status: ``BAD_REQUEST()``,
``NOT_FOUND()``, ``BAD_GATEWAY()`` and so on.

Handle exceptions with a handler. It receives the request and the exception, and
whatever it returns is sent as the response:

.. code-block:: python

    @app.on_error(ResponseError)
    async def on_error(request, error):
        if error.status_code == 404:
            return ResponseError.NOT_FOUND("Custom 404 Page")
        return error

Middleware
----------

A coroutine middleware wraps request handling. It receives the app callable
(further routing) and the raw ASGI arguments, so it can touch both the request
and the parsed response:

.. code-block:: python

    @app.middleware
    async def timing(app, request, receive, send):
        response = await app(request, receive, send)
        if response is not None:
            response.headers["x-custom-md"] = "passed"
        return response

``app(request, receive, send)`` returns a :class:`~muffin.Response`, or ``None``
for websockets where the handler writes directly.

Middleware runs in registration order, outermost first: the first registered
coroutine sees the request first and the response last. Pass
``insert_first=True`` to put a middleware in front of the ones already registered,
which is what error reporting and timing wrappers usually want:

.. code-block:: python

    app.middleware(timing, insert_first=True)

Anything else passed to ``app.middleware()`` is treated as ASGI middleware and
bound to the application's lifespan:

.. code-block:: python

    from sentry_asgi import SentryMiddleware

    app.middleware(SentryMiddleware)

Plugin middleware is appended when the plugin is bound, so it runs inside any
middleware registered before the plugin. Read the plugin docs when the order
matters.

Nested Applications
-------------------

An application can be mounted under a prefix:

.. code-block:: python

    subapp = Application()

    @subapp.route("/route")
    async def subroute(request):
        return "From subapp"

    app.route("/sub")(subapp)

``/sub/route`` is now handled by ``subapp``; its views see the trimmed path.

Host-Based Routing
------------------

Host matching is off by default. Turn it on and pass ``hosts`` to the routes
that need it:

.. code-block:: python

    app = Application(USE_HOSTS=True)

    @app.route("/", hosts=["example.com"])
    async def home(request):
        return "example.com only"

    @app.route("/")
    async def fallback(request):
        return "any host"

The ``Host`` header is compared lowercased and without the port. A route with
``hosts`` only matches the listed hosts, so a request with an unknown host falls
through to the routes without ``hosts`` and otherwise ends with a 404.

Startup and Shutdown
--------------------

Handlers registered with ``on_startup`` and ``on_shutdown`` run once per
application lifespan, before the first request and after the last one:

.. code-block:: python

    @app.on_startup
    async def connect():
        await pool.connect()

    @app.on_shutdown
    async def disconnect():
        await pool.close()

Plugins use the same hooks, so plugin resources are ready when views run.

Run Tasks After the Response
----------------------------

``run_after_response`` schedules awaitables that run once the response has been
sent: sending an email, writing a log entry, invalidating a cache:

.. code-block:: python

    async def send_email(address):
        await mailer.send(address, "Hello!")

    @app.route("/signup")
    async def signup(request):
        app.run_after_response(send_email("user@example.com"))
        return "Scheduled"

Tasks run to completion before the request cycle ends. A failing task is logged
and does not change the response. Call it from a view only: scheduling from
inside a background task has no effect, because the response has already gone.

Debug Mode
----------

.. code-block:: python

    app = Application(DEBUG=True)

Debug mode prints tracebacks to the console and lets exceptions propagate
instead of returning a 500 page.

Return Values
-------------

A view can return a response object or plain data; Muffin converts the rest:

1. :class:`~muffin.Response` is used as is
2. ``str``, ``bytes``: HTML response
3. ``dict``, ``list``, ``int``, ``bool``, ``None``: JSON response
4. ``(status, content)``: the status code is overridden
5. ``(status, headers, content)``: status and headers are applied

.. code-block:: python

    @app.route("/json")
    async def json_view(request):
        return {"key": "value"}

    @app.route("/html")
    async def html_view(request):
        return "<h1>Hello</h1>"

    @app.route("/created")
    async def created(request):
        return 201, {"Location": "/items/1"}, "Created"

Returning a full response, when content type or cookies matter:

.. code-block:: python

    from muffin import Response

    @app.route("/text")
    async def text(request):
        response = Response("plain text", content_type="text/plain")
        response.cookies["session"] = "xyz"
        return response

All response classes are listed in :doc:`api`.

.. _ASGI: https://asgi.readthedocs.io/en/latest/
