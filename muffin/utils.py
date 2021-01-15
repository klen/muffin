"""The Muffin Utils."""

import asyncio as aio
import importlib
import pkgutil
import sys


try:
    import trio
except ImportError:
    trio = None


__all__ = (
    'aio_lib', 'aio_run', 'import_submodules', 'current_async_library',
    'is_awaitable', 'to_awaitable'
)


def aio_lib():
    """Return current async library."""
    return trio or aio


def aio_run(coro):
    """Run the given coroutine with current async library."""
    lib = aio_lib()
    return lib.run(coro)


def import_submodules(package_name, *submodules):
    """Import all submodules by package name."""
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + '.' + name)
        for _, name, _ in pkgutil.walk_packages(package.__path__)
        if not submodules or name in submodules
    }


def import_app(app: str):
    """Import application by the given string (python.path.to.module:app_name)."""
    mod, _, name = app.partition(':')
    mod = importlib.import_module(mod)
    return getattr(mod, name, None) or getattr(mod, 'app', None) or getattr(mod, 'application')


from sniffio import current_async_library               # noqa
from asgi_tools.utils import is_awaitable, to_awaitable # noqa
