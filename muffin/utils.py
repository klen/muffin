"""The Muffin Utils."""

from __future__ import annotations

import asyncio
import importlib
import os
import pkgutil
import sys
import threading
from collections import OrderedDict
from contextlib import suppress
from logging import getLogger
from typing import TYPE_CHECKING, Callable, Coroutine, Iterable, TypeVar

from asgi_tools.utils import is_awaitable, to_awaitable
from sniffio import current_async_library

from muffin.errors import InvalidAppError

if TYPE_CHECKING:
    from types import ModuleType

    from .app import Application

__all__ = (
    "aio_lib",
    "aio_run",
    "current_async_library",
    "import_submodules",
    "is_awaitable",
    "logger",
    "to_awaitable",
)

AIOLIB = threading.local()
AIOLIB.current = None
AIOLIBS: dict[str, ModuleType] = OrderedDict()

with suppress(ImportError):
    import curio

    AIOLIBS["curio"] = curio

with suppress(ImportError):
    import trio

    AIOLIBS["trio"] = trio

AIOLIBS["asyncio"] = asyncio

TV = TypeVar("TV")

logger = getLogger("muffin")


def aio_lib() -> str:
    """Return first available async library."""
    aiolib = os.environ.get("MUFFIN_AIOLIB")
    if aiolib:
        return aiolib

    for name, module in AIOLIBS.items():
        if module is not None:
            return name

    return "asyncio"


def aio_run(corofn: Callable[..., Coroutine[None, None, TV]], *args, **kwargs) -> TV:
    """Run the given coroutine with current async library."""
    AIOLIB.current = aiolib = AIOLIB.current or aio_lib()
    if aiolib == "asyncio":
        return asyncio.run(corofn(*args, **kwargs))

    return AIOLIBS[aiolib].run(lambda: corofn(*args, **kwargs))


def import_submodules(
    package_name: str, *module_names: str, silent: bool = False, exclude: Iterable[str] = ()
) -> dict[str, ModuleType]:
    """Import all submodules by the given package name."""
    package = sys.modules[package_name]
    res = {}
    to_import = module_names or (name for _, name, _ in pkgutil.walk_packages(package.__path__))
    if exclude:
        to_import = (name for name in to_import if name not in exclude)

    for module_name in to_import:
        try:
            res[module_name] = importlib.import_module(f"{package_name}.{module_name}")
        except ImportError as exc:  # noqa: PERF203
            if not silent:
                raise

            logger.debug("Failed to import %s: %s", f"{package_name}.{module_name}", exc)

    return res


def import_app(app_uri: str, *, reload: bool = False) -> Application:
    """Import application by the given string (python.path.to.module:app_name)."""
    mod_name, _, app_name = app_uri.partition(":")
    mod = importlib.import_module(mod_name)
    if reload:
        importlib.reload(mod)

    try:
        return getattr(mod, app_name or "app", None) or mod.application
    except AttributeError as exc:
        raise InvalidAppError(app_uri) from exc
