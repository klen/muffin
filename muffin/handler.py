import asyncio
import re

import ujson as json
from aiohttp import web, multidict

from muffin.utils import to_coroutine

# TODO: aiohttp 0.15.2 swith method to * for Handler


RETYPE = type(re.compile('@'))
DYNS_RE = re.compile(r'(\{[^{}]*\})')
DYNR_RE = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)(?::(?P<re>.+))*\}$')

HTTP_METHODS = 'head', 'options', 'get', 'post', 'put', 'patch', 'delete'


class HandlerMeta(type):

    def __new__(mcs, name, bases, params):

        methods = set(params.get(
            'methods', sum([list(getattr(o, 'methods', [])) for o in bases], [])))

        for method in HTTP_METHODS:
            if method not in params:
                continue
            methods.add(method)
            params[method] = to_coroutine(params[method])

        if 'dispatch' in params:
            params['dispatch'] = to_coroutine(params['dispatch'])

        params['methods'] = methods
        params['name'] = params.get('name') or name.lower()

        return super(HandlerMeta, mcs).__new__(mcs, name, bases, params)


class Handler(object, metaclass=HandlerMeta):

    """ Handle request. """

    name = None

    def __init__(self, app):
        self.app = app
        self.loop = app._loop

    @classmethod
    def from_view(cls, view, *methods, name=None):
        """ Create handler class from function or coroutine. """
        view = to_coroutine(view)

        @asyncio.coroutine
        def method(self, *args, **kwargs):
            response = yield from view(*args, **kwargs)
            return response

        if "*" in methods:
            methods = HTTP_METHODS

        return type(name or view.__name__, (cls,), {m.lower(): method for m in methods})

    @classmethod
    def connect(cls, app, *paths, name=None):
        """ Connect to the application. """

        @asyncio.coroutine
        def view(request):
            handler = cls(app)
            response = yield from handler.dispatch(request)
            return response

        for method in cls.methods:
            name = name or cls.name
            lname = "%s-%s" % (name.lower(), method.lower())
            for num, path in enumerate(paths, 1):
                if isinstance(path, RETYPE):
                    app.router.register_route(RawReRoute(
                       method.upper(), view, lname, path))
                else:
                    app.router.add_route(method, path, view, name=lname)

                lname = "%s-%s" % (lname, num)

    @asyncio.coroutine
    def dispatch(self, request, **kwargs):
        """ Dispatch request. """
        method = getattr(self, request.method.lower())
        response = yield from method(request, **kwargs)
        return (yield from self.make_response(response))

    @asyncio.coroutine
    def make_response(self, response):
        """ Ensure that response is web.Response or convert it. """

        while asyncio.iscoroutine(response):
            response = yield from response

        if isinstance(response, web.Response):
            return response

        if isinstance(response, (multidict.MultiDict, multidict.MultiDictProxy)):
            response = dict(response)

        if isinstance(response, (list, dict)):
            return web.Response(text=json.dumps(response), content_type='application/json')

        return web.Response(text=str(response), content_type='text/html')

    def parse(self, request):
        """ Return data from request.

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


class RawReRoute(web.DynamicRoute):

    def __init__(self, method, handler, name, pattern):
        super().__init__(method, handler, name, pattern, None)

    def url(self, *, parts, query=None):
        raise NotImplemented

    def __repr__(self):
        name = "'" + self.name + "' " if self.name is not None else ""
        return "<RawReRoute {name}[{method}] {pattern} -> {handler!r}".format(
            name=name, method=self.method, pattern=self._pattern, handler=self.handler)


def sre(reg):
    reg = reg.strip('^$')

    def parse(match):
        [part] = match.groups()
        match = DYNR_RE.match(part)
        params = match.groupdict()
        return '(?P<%s>%s)' % (params['var'], params['re'] or '[^{}/]+')

    return re.compile('^%s$' % DYNS_RE.sub(parse, reg))
