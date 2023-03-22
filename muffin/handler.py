"""Muffin Handlers."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional, Tuple, Type, cast

from asgi_tools.utils import is_awaitable
from asgi_tools.view import HTTP_METHODS, HTTPView

from muffin.errors import AsyncRequiredError

if TYPE_CHECKING:
    from asgi_tools import Request
    from asgi_tools.types import TVCallable
    from http_router import Router
    from http_router.types import TMethods, TMethodsArg


class HandlerMeta(type):
    """Prepare handlers."""

    def __new__(
        mcs: Type[HandlerMeta],
        name: str,
        bases: Tuple[type],
        params: Dict[str, Any],
    ):
        """Prepare a Handler Class."""
        cls = cast(Type["Handler"], super().__new__(mcs, name, bases, params))

        # Ensure that the class methods are exist and iterable
        if not cls.methods:
            cls.methods = [method for method in HTTP_METHODS if method.lower() in cls.__dict__]

        elif isinstance(cls.methods, str):
            cls.methods = [cls.methods]

        cls.methods = {method.upper() for method in cls.methods}
        for m in cls.methods:
            method = getattr(cls, m.lower(), None)
            if method and not is_awaitable(method):
                raise AsyncRequiredError(method)

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

    methods: Optional[TMethods] = None

    @classmethod
    def __route__(
        cls,
        router: "Router",
        *paths: str,
        methods: Optional[TMethodsArg] = None,
        **params,
    ):
        """Check for registered methods."""
        router.bind(cls, *paths, methods=methods or cls.methods, **params)
        for _, method in inspect.getmembers(cls, lambda m: hasattr(m, "__route__")):
            cpaths, cparams = method.__route__
            router.bind(cls, *cpaths, __meth__=method.__name__, **cparams)

        return cls

    def __call__(self, request: "Request", **opts) -> Awaitable:
        """Dispatch the given request by HTTP method."""
        method = getattr(self, opts.get("__meth__") or request.method.lower())
        return method(request)

    @staticmethod
    def route(*paths: str, **params) -> Callable[[TVCallable], TVCallable]:
        """Mark a method as a route."""

        def wrapper(method):
            """Wrap a method."""
            method.__route__ = paths, params
            return method

        return wrapper


route_method = Handler.route
