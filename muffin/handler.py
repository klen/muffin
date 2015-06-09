""" Base handler class. """
import asyncio
import re

import ujson as json
from aiohttp import web, multidict

from muffin.urls import RawReRoute
from muffin.utils import to_coroutine, abcoroutine


# TODO: aiohttp 0.15.2 swith method to * for Handler


RETYPE = type(re.compile('@'))

HTTP_METHODS = 'head', 'options', 'get', 'post', 'put', 'patch', 'delete'


def register(router, view, path, method, name):
    """ Register URL path/re to router. """
    # Fix route name
    cname, num = name + "-" + method.lower(), 1
    while cname in router:
        cname = name + "-" + str(num)
        num += 1

    if isinstance(path, RETYPE):
        return router.register_route(RawReRoute(method.upper(), view, cname, path))

    return router.add_route(method, path, view, name=cname)


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


class Handler(object, metaclass=HandlerMeta):

    """ Handle request. """

    name = None
    methods = None

    def __init__(self, app):
        """ Initialize an application. """
        self.app = app

    @classmethod
    def from_view(cls, view, *methods, name=None):
        """ Create handler class from function or coroutine. """
        view = to_coroutine(view)

        def method(self, *args, **kwargs):
            return view(*args, **kwargs)

        if "*" in methods:
            methods = HTTP_METHODS

        return type(name or view.__name__, (cls,), {m.lower(): method for m in methods})

    @classmethod
    def connect(cls, app, *paths, methods=None, name=None, router=None):
        """ Connect to the application. """
        @asyncio.coroutine
        def view(request):
            handler = cls(app)
            response = yield from handler.dispatch(request)
            return response

        if router is None:
            router = app.router

        for method in methods or ["*"]:
            for path in paths:

                if isinstance(path, type) and issubclass(path, Exception):
                    app._error_handlers[path] = view
                    continue

                register(router, view, path, method, name or cls.name)

    @abcoroutine
    def dispatch(self, request, **kwargs):
        """ Dispatch request. """
        if request.method not in self.methods:
            raise web.HTTPMethodNotAllowed(request.method, self.methods)
        method = getattr(self, request.method.lower())
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
