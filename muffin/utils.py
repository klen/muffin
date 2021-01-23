"""The Muffin Utils."""

import asyncio as aio
import importlib
import pkgutil
import sys
import typing as t
from types import ModuleType

from asgi_tools.types import ASGIApp


try:
    import trio  # type: ignore
except ImportError:
    trio = None


__all__ = (
    'aio_lib', 'aio_run', 'import_submodules', 'current_async_library',
    'is_awaitable', 'to_awaitable'
)


def aio_lib() -> ModuleType:
    """Return current async library."""
    return trio or aio


def aio_run(corofn: t.Callable, *args, **kwargs) -> t.Any:
    """Run the given coroutine with current async library."""
    lib = aio_lib()
    if lib is aio:
        return aio.run(corofn(*args, **kwargs))

    return trio.run(corofn, *args, **kwargs)


def import_submodules(package_name: str, *submodules: str) -> t.Dict[str, ModuleType]:
    """Import all submodules by package name."""
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + '.' + name)
        for _, name, _ in pkgutil.walk_packages(package.__path__)  # type: ignore
        if not submodules or name in submodules
    }


def import_app(app: str) -> t.Optional[ASGIApp]:
    """Import application by the given string (python.path.to.module:app_name)."""
    mod_name, _, app_name = app.partition(':')
    mod = importlib.import_module(mod_name)
    return getattr(mod, app_name, None) or getattr(mod, 'app', None) or getattr(mod, 'application')


from sniffio import current_async_library               # noqa
from asgi_tools.utils import is_awaitable, to_awaitable # noqa
