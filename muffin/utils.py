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
from typing import TYPE_CHECKING, Callable, Coroutine, Dict, TypeVar

from asgi_tools.utils import is_awaitable, to_awaitable
from curio.task import logging
from sniffio import current_async_library

from muffin.errors import InvalidAppError

if TYPE_CHECKING:
    from types import ModuleType

    from .app import Application

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

with suppress(ImportError):
    import curio

    AIOLIBS["curio"] = curio

with suppress(ImportError):
    import trio

    AIOLIBS["trio"] = trio

AIOLIBS["asyncio"] = asyncio

TV = TypeVar("TV")

logger = logging.getLogger("muffin")


def aio_lib() -> str:
    """Return first available async library."""
    aiolib = os.environ.get("MUFFIN_AIOLIB", "asyncio")
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
    package_name: str, *module_names: str, silent: bool = False
) -> Dict[str, ModuleType]:
    """Import all submodules by the given package name."""
    package = sys.modules[package_name]
    res = {}
    for module_name in module_names or (
        name for _, name, _ in pkgutil.walk_packages(package.__path__)
    ):
        try:
            res[module_name] = importlib.import_module(f"{package_name}.{module_name}")
        except ImportError:
            if not silent:
                raise

            logger.debug("Failed to import module: %s", f"{package_name}.{module_name}")

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
