"""Muffin Handlers."""

import inspect
import typing as t

from http_router import Router
from http_router.typing import TYPE_METHODS
from asgi_tools import Request
from asgi_tools.app import HTTPView, HTTP_METHODS
from asgi_tools.utils import is_awaitable


class HandlerMeta(type):

    """Prepare handlers."""

    def __new__(mcs, name, bases, params):
        """Prepare a Handler Class."""
        cls = super().__new__(mcs, name, bases, params)

        # Ensure that the class methods are exist and iterable
        if not cls.methods:
            cls.methods = set(method for method in HTTP_METHODS if method.lower() in cls.__dict__)

        elif isinstance(cls.methods, str):
            cls.methods = [cls.methods]

        cls.methods = set(method.upper() for method in cls.methods)
        for m in cls.methods:
            method = getattr(cls, m.lower(), None)
            if method and not is_awaitable(method):
                raise TypeError("The method '%s' has to be awaitable" % method)

        return cls


class Handler(HTTPView, metaclass=HandlerMeta):

    """Class-based view pattern for handling HTTP method dispatching.

    .. code-block:: python

        @app.route('/hello', '/hello/{name}')
        class HelloHandler(Handler):

            async def get(self, request):
                name = request.patch_params.get('name') or 'all'
                return "GET: Hello f{name}"

            async def post(self, request):
                name = request.patch_params.get('name') or 'all'
                return "POST: Hello f{name}"

            @Handler.route('/hello/custom')
            async def custom(self, request):
                return 'Custom HELLO'

        # ...
        async def test_my_endpoint(client):
            response = await client.get('/hello')
            assert await response.text() == 'GET: Hello all'

            response = await client.get('/hello/john')
            assert await response.text() == 'GET: Hello john'

            response = await client.post('/hello')
            assert await response.text() == 'POST: Hello all'

            response = await client.get('/hello/custom')
            assert await response.text() == 'Custom HELLO'

            response = await client.delete('/hello')
            assert response.status_code == 405

    """

    methods: t.Optional[t.Sequence[str]] = None

    @classmethod
    def __route__(cls, router: Router, *paths: str, methods: TYPE_METHODS = None, **params):
        """Check for registered methods."""
        router.bind(cls, *paths, methods=methods or cls.methods, **params)
        for _, method in inspect.getmembers(cls, lambda m: hasattr(m, '__route__')):
            cpaths, cparams = method.__route__
            router.bind(cls, *cpaths, __meth__=method.__name__, **cparams)

        return cls

    def __call__(self, request: Request, *args, **opts) -> t.Awaitable:
        """Dispatch the given request by HTTP method."""
        method = getattr(self, opts.get('__meth__') or request.method.lower())
        return method(request)

    @staticmethod
    def route(*paths: str, **params) -> t.Callable:
        """Route custom methods for Handlers."""

        def wrapper(method):
            """Wrap a method."""
            method.__route__ = paths, params
            return method

        return wrapper
