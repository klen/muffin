"""Muffin Handlers."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from asgi_tools.view import HTTPView

from muffin.errors import AsyncRequiredError

if TYPE_CHECKING:
    from asgi_tools import Request
    from asgi_tools.types import TVCallable
    from http_router import Router
    from http_router.types import THostsArg, TMethods, TMethodsArg


class HandlerMeta(type):
    """Prepare handlers."""

    def __new__(mcs: type[HandlerMeta], name: str, bases: tuple[type], params: dict[str, Any]):
        """Prepare a Handler Class."""
        cls = cast("type[Handler]", super().__new__(mcs, name, bases, params))

        # Normalize methods: explicit or inherited, no auto-detection.
        methods = cls.methods
        if isinstance(methods, str):
            methods = [methods]

        cls.methods = {method.upper() for method in methods or []}
        for m in cls.methods:
            method = getattr(cls, m.lower(), None)
            if method and not inspect.iscoroutinefunction(method):
                raise AsyncRequiredError(method)

        return cls


class Handler(HTTPView, metaclass=HandlerMeta):
    """Class-based view pattern for handling HTTP method dispatching.

    Methods must be set explicitly (``methods``) or inherited from a parent
    class. There is no automatic detection: defining ``async def get`` does not
    register ``GET`` on its own.

    .. code-block:: python

        @app.route('/hello', '/hello/{name}')
        class HelloHandler(Handler):
            methods = ['get', 'post']

            async def get(self, request):
                name = request.patch_params.get('name') or 'all'
                return f"GET: Hello {name}"

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

    methods: TMethods | None = None

    @classmethod
    def __route__(  # type: ignore[override]
        cls,
        router: Router,
        *paths: str,
        methods: TMethodsArg | None = None,
        hosts: THostsArg | None = None,
        **params,
    ):
        """Check for registered methods."""
        router.bind(cls, *paths, methods=methods or cls.methods, hosts=hosts, **params)
        for _, method in inspect.getmembers(cls, lambda m: hasattr(m, "__route__")):
            paths, methods, hosts = method.__route__
            router.bind(cls, *paths, methods=methods, hosts=hosts, method_name=method.__name__)

        return cls

    def __call__(self, request: Request, *, method_name: str | None = None, **_) -> Awaitable:
        """Dispatch the given request by HTTP method."""
        method = getattr(self, method_name or request.method.lower())
        return method(request)

    @staticmethod
    def route(
        *paths: str, methods: TMethodsArg | None = None, hosts: THostsArg | None = None
    ) -> Callable[[TVCallable], TVCallable]:
        """Mark a method as a route."""

        def wrapper(method):
            """Wrap a method."""
            method.__route__ = paths, methods, hosts
            return method

        return wrapper


route_method = Handler.route
