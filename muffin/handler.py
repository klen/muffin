""" Base handler class. """
import asyncio

import ujson as json
from aiohttp import web, multidict
from collections import defaultdict

from muffin.urls import routes_register
from muffin.utils import to_coroutine, abcoroutine


HTTP_METHODS = 'head', 'options', 'get', 'post', 'put', 'patch', 'delete'


class HandlerMeta(type):

    """ Prepare handlers. """

    coroutines = set(HTTP_METHODS)

    def __new__(mcs, name, bases, params):
        """ Check for handler is correct. """
        # Define new coroutines
        for fname, method in params.items():
            if callable(method) and hasattr(method, '_abcoroutine'):
                mcs.coroutines.add(fname)

        # Set name
        params['name'] = params.get('name', name.lower())

        cls = super(HandlerMeta, mcs).__new__(mcs, name, bases, params)

        # Set a class methods
        if isinstance(cls.methods, str):
            cls.methods = [cls.methods]

        if not cls.methods:
            cls.methods = set(method for method in HTTP_METHODS if method in cls.__dict__)

        cls.methods = [method.upper() for method in cls.methods]

        # Ensure that coroutine methods is coroutines
        for name in mcs.coroutines:
            method = getattr(cls, name, None)
            if not method:
                continue
            setattr(cls, name, to_coroutine(method))

        return cls


class DummyApp:

    def __init__(self):
        self.callbacks = defaultdict(list)

    def register(self, *args, handler=None, **kwargs):
        def wrapper(func):
            self.callbacks[handler].append((args, kwargs, func))
            return func
        return wrapper

    def install(self, app, handler):
        for args, kwargs, func in self.callbacks[handler]:
            app.register(*args, handler=handler, **kwargs)(func)
        del self.callbacks[handler]


class Handler(object, metaclass=HandlerMeta):

    """ Handle request. """

    app = DummyApp()
    name = None
    methods = None

    @classmethod
    def from_view(cls, view, *methods, name=None):
        """ Create handler class from function or coroutine. """
        view = to_coroutine(view)

        def method(self, *args, **kwargs):
            return view(*args, **kwargs)

        if web.hdrs.METH_ANY in methods:
            methods = HTTP_METHODS

        return type(name or view.__name__, (cls,), {m.lower(): method for m in methods})

    @classmethod
    def connect(cls, app, *paths, methods=None, name=None, router=None, view=None):
        """ Connect to the application. """
        if isinstance(cls.app, DummyApp):
            cls.app, dummy = app, cls.app
            dummy.install(app, cls)

        @asyncio.coroutine
        def handle(request):
            return (yield from cls().dispatch(request, view=view))

        if not paths:
            paths = ["/%s" % cls.__name__]

        routes_register(app, handle, *paths, methods=methods, router=router, name=name or cls.name)

    @classmethod
    def register(cls, *args, **kwargs):
        """ Register view to handler. """
        return cls.app.register(*args, handler=cls, **kwargs)

    @abcoroutine
    def dispatch(self, request, view=None, **kwargs):
        """ Dispatch request. """
        if request.method not in self.methods:
            raise web.HTTPMethodNotAllowed(request.method, self.methods)

        method = getattr(self, view or request.method.lower())
        response = yield from method(request, **kwargs)

        return (yield from self.make_response(request, response))

    @abcoroutine
    def make_response(self, request, response):
        """ Ensure that response is web.Response or convert it. """
        while asyncio.iscoroutine(response):
            response = yield from response

        if isinstance(response, web.StreamResponse):
            return response

        if isinstance(response, str):
            return web.Response(text=response, content_type='text/html')

        if isinstance(response, (list, dict)):
            return web.Response(text=json.dumps(response), content_type='application/json')

        if isinstance(response, (multidict.MultiDict, multidict.MultiDictProxy)):
            response = dict(response)
            return web.Response(text=json.dumps(response), content_type='application/json')

        if isinstance(response, bytes):
            response = web.Response(body=response, content_type='text/html')
            response.charset = self.app.cfg.ENCODING
            return response

        elif response is None:
            response = ''

        return web.Response(text=str(response), content_type='text/html')

    def parse(self, request):
        """ Return a coroutine which parse data from request depended on content-type.

        Usage: ::

            # ...

            def post(self, request):
                data = yield from self.parse(request)
                # ...

        """
        if request.content_type in ('application/x-www-form-urlencoded', 'multipart/form-data'):
            return request.post()

        if request.content_type == 'application/json':
            return request.json()

        return request.text()
