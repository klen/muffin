"""A helper to write Muffin Plugins."""

from __future__ import annotations

from abc import ABC
from asyncio import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Mapping

from modconfig import Config

from muffin.errors import MuffinError

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from muffin.app import Application


class PluginError(MuffinError):
    """Implement any exception in plugins."""


class PluginNotInstalledError(RuntimeError):
    """Raised when a plugin is not installed."""


class BasePlugin(ABC):
    """Base class for Muffin plugins."""

    name: str

    # Plugin options with default values
    defaults: ClassVar[Mapping[str, Any]] = {"disabled": False}

    # Optional middleware method
    middleware: Callable[..., Awaitable] | None = None

    # Optional startup method
    startup: Callable[..., Awaitable] | None = None

    # Optional shutdown method
    shutdown: Callable[..., Awaitable] | None = None

    # Optional conftest method
    conftest: Callable[[], AbstractAsyncContextManager] | None = None

    def __init__(self, app: Application | None = None, **options):
        """Save application and create he plugin's configuration."""
        if getattr(self, "name", None) is None:
            msg = "Plugin.name is required"
            raise TypeError(msg)

        self.cfg = Config(
            config_config={"update_from_env": False}, **dict({"disabled": False}, **self.defaults)
        )
        self.__app__ = app

        if app is not None:
            self.setup(app, **options)
        else:
            self.cfg.update_from_dict(options, exist_only=True)

    def __repr__(self) -> str:
        """Human readable representation."""
        return f"<muffin.Plugin: { self.name }>"

    async def __aenter__(self):
        if iscoroutinefunction(self.startup):
            await self.startup()

    async def __aexit__(self, exc_type, exc, tb):
        if iscoroutinefunction(self.shutdown):
            await self.shutdown()

    @property
    def app(self) -> Application:
        """Get the application."""
        if self.__app__ is None:
            raise PluginNotInstalledError()

        return self.__app__

    def setup(self, app: Application, *, name: str | None = None, **options) -> Any:
        """Bind app and update the plugin's configuration."""
        # allow to redefine the name for multi plugins with same type
        self.name = name or self.name

        # Update configuration
        self.cfg.update_from_dict(
            dict(app.cfg),
            prefix=f"{self.name}_",
            exist_only=True,
        )
        self.cfg.update_from_dict(options)
        if self.cfg.disabled:
            app.logger.warning("Plugin %s is disabled", self.name)
            return False

        app.plugins[self.name] = self
        self.__app__ = app

        # Register a middleware
        if callable(self.middleware):
            app.middleware(self.middleware)

        # Bind startup
        if callable(self.startup):
            app.on_startup(self.startup)

        # Bind shutdown
        if callable(self.shutdown):
            app.on_shutdown(self.shutdown)

        return True

    async def restart(self):
        if callable(self.shutdown):
            await self.shutdown()

        if callable(self.startup):
            await self.startup()
