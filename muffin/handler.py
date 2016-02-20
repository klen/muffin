"""Base handler class."""
import inspect
import functools
from asyncio import coroutine, iscoroutine

import ujson as json
from aiohttp.hdrs import METH_ANY
from aiohttp.multidict import MultiDict, MultiDictProxy
from aiohttp.web import StreamResponse, HTTPMethodNotAllowed, Response, View

from muffin.urls import routes_register
from muffin.utils import to_coroutine, abcoroutine


HTTP_METHODS = 'HEAD', 'OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
ROUTE_PARAMS_ATTR = '_route_params'


def register(*paths, methods=None, name=None, handler=None):
    """Mark Handler.method to aiohttp handler.

    It uses when registration of the handler with application is postponed.

    ::
        class AwesomeHandler(Handler):

            def get(self, request):
                return "I'm awesome!"

            @register('/awesome/best')
            def best(self, request):
                return "I'm best!"

    """
    def wrapper(method):
        """Store route params into method."""
        method = to_coroutine(method)
        setattr(method, ROUTE_PARAMS_ATTR, (paths, methods, name))
        if handler and not hasattr(handler, method.__name__):
            setattr(handler, method.__name__, method)
        return method
    return wrapper


class HandlerMeta(type):

    """Prepare handlers."""

    _coroutines = set(m.lower() for m in HTTP_METHODS)

    def __new__(mcs, name, bases, params):
        """Prepare a Handler Class.

        Ensure that the Handler class has a name.
        Ensure that required methods are coroutines.
        Fix the Handler params.
        """
        # Set name
        params['name'] = params.get('name', name.lower())

        # Define new coroutines
        for fname, method in params.items():
            if callable(method) and hasattr(method, '_abcoroutine'):
                mcs._coroutines.add(fname)

        cls = super(HandlerMeta, mcs).__new__(mcs, name, bases, params)

        # Ensure that the class methods are exist and iterable
        if not cls.methods:
            cls.methods = set(method for method in HTTP_METHODS if method.lower() in cls.__dict__)

        elif isinstance(cls.methods, str):
            cls.methods = [cls.methods]

        cls.methods = [method.upper() for method in cls.methods]

        # Ensure that coroutine methods is coroutines
        for name in mcs._coroutines:
            method = getattr(cls, name, None)
            if not method:
                continue
            setattr(cls, name, to_coroutine(method))

        return cls


class Handler(object, metaclass=HandlerMeta):

    """Handle request."""

    app = None
    name = None
    methods = None

    @classmethod
    def from_view(cls, view, *methods, name=None):
        """Create a handler class from function or coroutine."""
        view = to_coroutine(view)

        if METH_ANY in methods:
            methods = HTTP_METHODS

        def proxy(self, *args, **kwargs):
            return view(*args, **kwargs)

        params = {m.lower(): proxy for m in methods}
        params['methods'] = methods
        return type(name or view.__name__, (cls,), params)

    @classmethod
    def connect(cls, app, *paths, methods=None, name=None, router=None, view=None):
        """Connect to the given application."""
        cls.app = app

        if cls.app is not None:
            for _, m in inspect.getmembers(cls, predicate=inspect.isfunction):
                if not hasattr(m, ROUTE_PARAMS_ATTR):
                    continue
                paths_, methods_, name_ = getattr(m, ROUTE_PARAMS_ATTR)
                name_ = name_ or ("%s.%s" % (cls.name, m.__name__))
                delattr(m, ROUTE_PARAMS_ATTR)
                cls.app.register(*paths_, methods=methods_, name=name_, handler=cls)(m)

        @coroutine
        @functools.wraps(cls)
        def handler(request):
            return cls().dispatch(request, view=view)

        if not paths:
            paths = ["/%s" % cls.__name__]

        return routes_register(
            app, handler, *paths, methods=methods, router=router, name=name or cls.name)

    @classmethod
    def register(cls, *args, **kwargs):
        """Register view to handler."""
        if cls.app is None:
            return register(*args, handler=cls, **kwargs)
        return cls.app.register(*args, handler=cls, **kwargs)

    @abcoroutine
    def dispatch(self, request, view=None, **kwargs):
        """Dispatch request."""
        if view is None and request.method not in self.methods:
            raise HTTPMethodNotAllowed(request.method, self.methods)

        method = getattr(self, view or request.method.lower())
        response = yield from method(request, **kwargs)

        return (yield from self.make_response(request, response))

    __iter__ = dispatch

    @abcoroutine
    def make_response(self, request, response):
        """Convert a handler result to web response."""
        while iscoroutine(response):
            response = yield from response

        if isinstance(response, StreamResponse):
            return response

        if isinstance(response, str):
            return Response(text=response, content_type='text/html', charset=self.app.cfg.ENCODING)

        if isinstance(response, (list, dict)):
            return Response(text=json.dumps(response), content_type='application/json')

        if isinstance(response, (MultiDict, MultiDictProxy)):
            response = dict(response)
            return Response(text=json.dumps(response), content_type='application/json')

        if isinstance(response, bytes):
            response = Response(
                body=response, content_type='text/html', charset=self.app.cfg.ENCODING)
            return response

        if response is None:
            response = ''

        return Response(text=str(response), content_type='text/html')

    @staticmethod
    def parse(request):
        """Return a coroutine which parses data from request depends on content-type.

        Usage: ::

            def post(self, request):
                data = yield from self.parse(request)
                # ...
        """
        if request.content_type in ('application/x-www-form-urlencoded', 'multipart/form-data'):
            return request.post()

        if request.content_type == 'application/json':
            return request.json()

        return request.text()
