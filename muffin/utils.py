"""The Muffin Utils."""

import asyncio
import importlib
import os
import pkgutil
import sys
import threading
from collections import OrderedDict
from types import ModuleType
from typing import Awaitable, Callable, Dict, TypeVar

from asgi_tools._compat import curio, trio
from asgi_tools.typing import ASGIApp

__all__ = (
    "aio_lib",
    "aio_run",
    "import_submodules",
    "current_async_library",
    "is_awaitable",
    "to_awaitable",
)

AIOLIB = threading.local()
AIOLIB.current = None
AIOLIBS: Dict[str, ModuleType] = OrderedDict()

if curio:
    AIOLIBS["curio"] = curio

if trio:
    AIOLIBS["trio"] = trio

AIOLIBS["asyncio"] = asyncio

Tv = TypeVar("Tv")


def aio_lib() -> str:
    """Return first available async library."""
    aiolib = os.environ.get("MUFFIN_AIOLIB", "asyncio")
    if aiolib:
        return aiolib

    for name, module in AIOLIBS.items():
        if module is not None:
            return name

    return "asyncio"


def aio_run(corofn: Callable[..., Awaitable[Tv]], *args, **kwargs) -> Tv:
    """Run the given coroutine with current async library."""
    AIOLIB.current = aiolib = AIOLIB.current or aio_lib()
    if aiolib == "asyncio":
        return asyncio.run(corofn(*args, **kwargs))  # type: ignore

    return AIOLIBS[aiolib].run(lambda: corofn(*args, **kwargs))  # type: ignore


def import_submodules(package_name: str, *submodules: str) -> Dict[str, ModuleType]:
    """Import all submodules by package name."""
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + "." + name)
        for _, name, _ in pkgutil.walk_packages(package.__path__)  # type: ignore # mypy #1422
        if not submodules or name in submodules
    }


def import_app(app_uri: str, reload: bool = False) -> ASGIApp:
    """Import application by the given string (python.path.to.module:app_name)."""
    mod_name, _, app_name = app_uri.partition(":")
    mod = importlib.import_module(mod_name)
    if reload:
        importlib.reload(mod)

    try:
        return getattr(mod, app_name or "app", None) or getattr(mod, "application")
    except AttributeError as exc:
        raise ImportError(f"Application {app_uri} not found") from exc


from asgi_tools.utils import is_awaitable, to_awaitable  # noqa
from sniffio import current_async_library  # noqa
