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

Save this as :file:`hello.py`.

Run with:

.. code-block:: bash

    uvicorn hello:app

Visit http://127.0.0.1:8000/ to see your greeting.

Request Object
--------------

Every view receives a :class:`~muffin.Request` object:

.. code-block:: python

    @app.route('/login', methods=['POST'])
    async def login(request):
        form = await request.form()
        username = form.get('username')
        password = form.get('password')
        if username == 'admin':
            return f"Welcome, {username}"
        return "Invalid credentials"

Query parameters:

.. code-block:: python

    search = request.query.get('search', '')

Cookies:

.. code-block:: python

    session = request.cookies.get('session')

File uploads:

.. code-block:: python

    form = await request.form()
    file = form['file']
    content = await file.read()

Routing
-------

Define routes:

.. code-block:: python

    @app.route('/')
    async def index(request):
        return 'Index Page'

Dynamic routes:

.. code-block:: python

    @app.route('/user/{username}')
    async def user_profile(request):
        username = request.path_params['username']
        return f"Hello, {username}"

Type converters:

========= ====================================
``str``   (default) accepts any text without a slash
``int``   accepts positive integers
``float`` accepts positive floating point values
``path``  like string but also accepts slashes
``uuid``  accepts UUID strings
========= ====================================

Example:

.. code-block:: python

    @app.route('/post/{post_id:int}')
    async def post(request):
        post_id = request.path_params['post_id']
        return f"Post #{post_id}"

Regex routes:

.. code-block:: python

    import re

    @app.route(re.compile(r'/item/(a|b|c)/'))
    async def item(request):
        return request.path

Static Files
------------

Configure static files:

.. code-block:: python

    app = Application(static_url_prefix='/assets', static_folders=['static'])

Files are served at `/assets/{file}`.

Redirects and Errors
--------------------

Redirect example:

.. code-block:: python

    from muffin import ResponseRedirect

    @app.route('/')
    async def index(request):
        raise ResponseRedirect('/login')

Raise HTTP errors:

.. code-block:: python

    from muffin import ResponseError

    @app.route('/secure')
    async def secure(request):
        if not request.cookies.get('auth'):
            raise ResponseError.UNAUTHORIZED()
        return "Secret data"

Custom error handler:

.. code-block:: python

    @app.on_error(404)
    async def not_found(request, error):
        return "Custom 404 Page"

Middlewares
-----------

External ASGI middleware:

.. code-block:: python

    from sentry_asgi import SentryMiddleware

    app.middleware(SentryMiddleware)

Internal middleware:

.. code-block:: python

    @app.middleware
    async def simple_md(app, request, receive, send):
        response = await app(request, receive, send)
        response.headers['x-custom-md'] = 'passed'
        return response

Nested Applications
-------------------

Mount sub-applications for modular design:

.. code-block:: python

    subapp = Application()

    @subapp.route('/route')
    async def subroute(request):
        return "From subapp"

    app.route('/sub')(subapp)

Accessing `/sub/route` calls the sub-application route.

Run Tasks in Background
------------------------

Schedule background tasks after response is sent:

.. code-block:: python

    import asyncio

    async def background_task(param):
        await asyncio.sleep(1)
        print(f"Done: {param}")

    @app.route('/bg')
    async def bg(request):
        app.run_after_response(background_task("task"))
        return "Scheduled"

Debug Mode
----------

Enable debug mode for detailed error output:

.. code-block:: python

    app = Application(debug=True)

This prints tracebacks to console during development.

About Responses
---------------

Return values from views are automatically converted:

1. :class:`~muffin.Response` is returned as-is
2. `str` → HTML response
3. `dict`, `list`, `bool`, `None` → JSON response
4. `(status, content)` tuple → overrides status
5. `(status, content, headers)` tuple → adds headers

Example:

.. code-block:: python

    @app.route('/json')
    async def json_view(request):
        return {'key': 'value'}

    @app.route('/html')
    async def html_view(request):
        return '<h1>Hello</h1>'

    @app.route('/tuple')
    async def tuple_view(request):
        return 201, 'Created'

.. _ASGI: https://asgi.readthedocs.io/en/latest/
