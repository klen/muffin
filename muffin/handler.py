import asyncio

import ujson as json
from aiohttp import web

from muffin.utils import to_coroutine


class HandlerMeta(type):

    methods = 'head', 'options', 'get', 'post', 'put', 'patch', 'delete'

    def __new__(mcs, name, bases, params):

        def _handler(self, request):
            raise web.HTTPMethodNotAllowed

        params.setdefault('methods', mcs.methods)

        for method in params['methods']:
            params[method] = to_coroutine(params.get(method, _handler))

        if 'dispatch' in params:
            params['dispatch'] = to_coroutine(params['dispatch'])

        params['name'] = params.get('name') or name.lower()

        return super(HandlerMeta, mcs).__new__(mcs, name, bases, params)


class Handler(object, metaclass=HandlerMeta):

    """ Handle request. """

    name = None

    def __init__(self, app):
        self.app = app

    @classmethod
    def from_view(cls, view, *methods, name=None):
        """ Create handler class from function or coroutine. """
        view = to_coroutine(view)

        @asyncio.coroutine
        def method(self, *args, **kwargs):
            response = yield from view(*args, **kwargs)
            return response

        return type(name or view.__name__, (cls,), {m.lower(): method for m in methods})

    @classmethod
    def connect(cls, app, *paths, name=None):
        """ Connect to the application. """
        def view(request):
            handler = cls(app)
            response = yield from handler.dispatch(request)
            return response

        for method in cls.methods:
            name = name or cls.name
            name = "%s-%s" % (name.lower(), method.lower())
            lname = name
            for num, path in enumerate(paths, 1):
                app.router.add_route(method, path, view, name=lname)

                lname = "%s-%s" % (name, num)

    @asyncio.coroutine
    def dispatch(self, request):
        """ Dispatch request. """
        method = getattr(self, request.method.lower())
        response = yield from method(request)
        return (yield from self.make_response(response))

    @asyncio.coroutine
    def make_response(self, response):
        """ Ensure that response is web.Response or convert it. """

        while asyncio.iscoroutine(response):
            response = yield from response

        if isinstance(response, (list, dict)):
            return web.Response(text=json.dumps(response), content_type='application/json')

        if not isinstance(response, web.Response):
            return web.Response(text=str(response), content_type='text/html')

        return response
