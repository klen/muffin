Usage
=====

Quickstart
----------

.. code-block:: python

    from muffin import Application

    # Create the muffin's application
    app = Application()

    # Create view and bind it to http path "/"
    @app.route("/")
    async def hello_world(request):
        return "<p>Hello, World!</p>"

Save it as :file:`hello.py` or something similar.

To run the application, run the command:

.. code-block:: python

   uvicorn hello:app

This launches a very simple builtin server, which is good enough for
testing but probably not what you want to use in production.

Now head over to http://127.0.0.1:8000/, and you should see your hello
world greeting.

The Request Object
------------------

Every view should accept a request object.  The request object is
documented in the API section and we will not cover it here in detail (see
:class:`~muffin.Request`). Here is a broad overview of some of the most
common operations.

The current request method is available by using the
:attr:`~muffin.Request.method` attribute.  To access form data (data
transmitted in a ``POST`` or ``PUT`` request) you can use the
:attr:`~muffin.Request.form` attribute.  Here is a full example of the two
attributes mentioned above:

.. code-block:: python

   @app.route('/login', methods=['POST', 'PUT'])
    async def login(request):
        error = None
        if request.method == 'POST':
            formdata = await request.form()
            if valid_login(formdata['username'], formdata['password']):
                return log_the_user_in(formdata['username'])

            error = 'Invalid username/password'

        # Let's assume that you have Muffin-Jinja2 plugin enabled
        return await jinja2.render('login.html', error=error)

To access parameters submitted in the URL (``?key=value``) you can use the
:attr:`~muffin.Request.query` attribute:

.. code-block:: python

    search = request.query.get('search', '')

We recommend accessing URL parameters with `get` or by catching the
:exc:`KeyError` because users might change the URL and presenting them a 400
bad request page in that case is not user friendly.

For a full list of methods and attributes of the request object, head over
to the :class:`~muffin.Request` documentation.

Cookies
```````

Cookies are exposed as a regular dictionary interface through :attr:`~muffin.Request.cookies`:

.. code-block:: python

    session = request.cookies.get('session', '')

File Uploads
````````````

Request files are normally sent as multipart form data (`multipart/form-data`).
The uploaded files are available in :meth:`~muffin.Request.form`:

.. code-block:: python

    formdata = await request.form()

Routing
-------

Modern web applications use meaningful URLs to help users. Users are more
likely to like a page and come back if the page uses a meaningful URL they can
remember and use to directly visit a page.

Use the :meth:`~muffin.Application.route` decorator to bind a function to a URL.

.. code-block:: python

    @app.route('/')
    async def index():
        return 'Index Page'

    @app.route('/hello', '/hello/world')
    async def hello():
        return 'Hello, World'

    @app.route('/only-post', methods=['POST'])
    async def only_post():
        return request.method

You can do more! You can make parts of the URL dynamic.  The every routed
callback should be callable and accepts a :class:`~muffin.Request`.

See also: :py:class:`~muffin.Handler`.

Dynamic URLs
------------

All the URLs support regexp. You can use any regular expression to customize your URLs:

.. code-block:: python

   import re

    @app.route(re.compile(r'/reg/(a|b|c)/?'))
    async def regexp(request):
        return request.path

Variable Rules
``````````````

You can add variable sections to a URL by marking sections with
``<variable_name>``. Your function then receives the ``<variable_name>`` from
``request.path_params``.

.. code-block:: python

    @app.route('/user/{username}')
    async def show_user_profile(request):
        username = request.path_params['username']
        return f'User {username}'

By default this will capture characters up to the end of the path or the next /.

Optionally, you can use a converter to specify the type of the argument like
``<variable_name:converter>``.

Converter types:

========= ====================================
``str``   (default) accepts any text without a slash
``int``   accepts positive integers
``float`` accepts positive floating point values
``path``  like string but also accepts slashes
``uuid``  accepts UUID strings
========= ====================================

Convertors are used by prefixing them with a colon, like so:

.. code-block:: python

    @app.route('/post/{post_id:int}')
    async def show_post(request):
        post_id = request.path_params['post_id']
        return f'Post # {post_id}'

Any unknown convertor will be parsed as a regex:

.. code:: python

    @app.route('/orders/{order_id:\d{3}}')
    async def orders(request):
        order_id = request.path_params['order_id']
        return f'Order # {order_id}'


Static Files
------------

Set static url prefix and directories when initializing your app:

.. code-block:: python

    from muffin import Application

    app = Application(static_url_prefix='/assets', static_folders=['static'])

And your static files will be available at url ``/static/{file}``.


Redirects and Errors
--------------------

To redirect a user to another endpoint, use the :class:`~.muffin.ResponseRedirect`
class; to abort a request early with an error code, use the
:func:`~muffin.ResponseError` class:

.. code-block:: python

    from muffin import ResponseRedirect, ResponseError

    @app.route('/')
    async def index(request):
        return ResponseRedirect('/login')

    @app.route('/login')
    async def login(request):
        raise ResponseError(status_code=401)
        this_is_never_executed()

This is a rather pointless example because a user will be redirected from
the index to a page they cannot access (401 means access denied) but it
shows how that works.

By default only description is shown for each error code.  If you want to
customize the error page, you can use the :meth:`~muffin.App.on_error`
decorator:

.. code-block:: python

    @app.on_error(404)
    async def page_not_found(request, error):
        return render_template('page_not_found.html'), 404

It's possible to bind the handlers not only for status codes, but for the
exceptions themself:

.. code-block:: python

    @app.on_error(TimeoutError)
    async def timeout(request, error):
        return 'Something bad happens'

.. _about-responses:

About Responses
---------------

The return value from a view function is automatically converted into a
response object for you. If the return value is a string it's converted into a
response object with the string as response body, a ``200 OK`` status code and
a :mimetype:`text/html` mimetype. If the return value is a dict or list,
:func:`json.dumps` is called to produce a response.  The logic that Muffin
applies to converting return values into response objects is as follows:

1.  If a result is response :class:`~muffin.Response` it's directly
    returned from the view.
2.  If it's a string, a response :class:`~muffin.ResponseHTML` is created with
    that data and the default parameters.
3.  If it's a dict/list/bool/None, a response :class:`~muffin.ResponseJSON`
    is created
4.  If a tuple is returned the items in the tuple can provide extra
    information. Such tuples have to be in the form ``(status, response
    content)``, ``(status, response content, headers)``.  The
    ``status``:``int`` value will override the status code and
    ``headers``:``dict[str, str]`` a list or dictionary of additional header
    values.
5.  If none of that works, Muffin will convert the return value to a string
    and return as html.


.. code-block:: python

    @app.route('/html')
    async def html(request):
        return '<b>HTML is here</b>'

    @app.route('/json')
    async def json(request):
        return {'json': 'here'}

    @app.route('/text')
    async def text(request):
        res = ResponseText('response is here')
        res.headers['x-custom'] = 'value'
        res.cookies['x-custom'] = 'value'
        return res

    @app.route('/short-form')
    async def short_form(request):
        return 418, 'Im a teapot'

Middlewares
-----------

A Muffin application supports middlewares, which provide a flexible way to
define a chain of functions that handles every web requests.

1. As an ASGI_ application :py:class:`~muffin.Application` can be proxied with
   any ASGI_ middleware:

   .. code-block:: python

        from muffin import Application
        from sentry_asgi import SentryMiddleware

        app = Application()
        app = SentryMiddleware(app)

2. Alternatively you can decorate any ASGI_ middleware to connect it to an app:

   .. code-block:: python

        from muffin import Application
        from sentry_asgi import SentryMiddleware

        app = Application()
        app.middleware(SentryMiddleware)

3. Internal middlewares. For middlewares it's possible to use simpler interface
   which one accepts a request and can return responses.

   .. code-block:: python

        from muffin import Application


        app = Application()

        @app.middleware
        async def simple_md(app, request, receive, send):
            try:
                response = await app(request, receive, send)
                response.headers['x-simple-md'] = 'passed'
                return response
            except RuntimeError:
                return ResponseHTML('Middleware Exception')

Nested applications
-------------------

Sub applications are designed for solving the problem of the big monolithic
code base.

.. code-block:: python

    from muffin import Application

    # Main application
    app = Application()

    @app.route('/')
    def index(request):
        return 'OK'

    # Sub application
    subapp = Application()

    @subapp.route('/route')
    def subpage(request):
        return 'OK from subapp'

    # Connect the subapplication with an URL prefix
    app.route('/sub')(subapp)

    # await client.get('/sub/route').text() == 'OK from subapp'

Middlewares from app and subapp are chained (only internal middlewares are
supported for nested apps).

Run tasks in background
-----------------------

Muffin provides a simple way to run tasks in background: `Application.run_after_response`

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.task
    def send_email(email, message):
        # send email here
        pass

    @app.route('/send')
    async def send(request):

      # Schedule any awaitable for later execution
      app.run_after_response(send_email('user@email.com', 'Hello from Muffin!'))

      # Return response to a client immediately
      # The task will be executed after the response is sent
      return "OK"

Debug Mode
----------

Sometime there are errors in your code. If any exception happens when Muffin
processing a request, the library returns HTTP 500 page (the page is
customisible). If you want to see the errors in console, you are able to start
an application in debug mode.

.. code-block:: python

   app = Application(debug=True)  # as other options, this one could be defined in configuration modules


.. _ASGI: https://asgi.readthedocs.io/en/latest/
