"""A helper to write Muffin Plugins."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

from asgi_tools.utils import to_awaitable
from modconfig import Config

from muffin.errors import MuffinError

if TYPE_CHECKING:
    from contextlib import _AsyncGeneratorContextManager

    from muffin.app import Application


class PluginError(MuffinError):
    """Implement any exception in plugins."""


class PluginNotInstalledError(RuntimeError):
    """Raised when a plugin is not installed."""


class BasePlugin(ABC):
    """Base class for Muffin plugins."""

    name: str

    # Plugin options with default values
    defaults: Mapping[str, Any] = {}

    # Optional middleware method
    middleware: Optional[Callable] = None

    # Optional startup method
    startup: Optional[Callable] = None

    # Optional shutdown method
    shutdown: Optional[Callable] = None

    # Optional conftest method
    conftest: Optional[Callable[[], _AsyncGeneratorContextManager]] = None

    def __init__(self, app: Optional[Application] = None, **options):
        """Save application and create he plugin's configuration."""
        if getattr(self, "name", None) is None:
            msg = "Plugin.name is required"
            raise TypeError(msg)

        self.cfg = Config(config_config={"update_from_env": False}, disabled=False, **self.defaults)
        self.__app__ = app

        if app is not None:
            self.setup(app, **options)
        else:
            self.cfg.update_from_dict(options, exist_only=True)

    def __repr__(self) -> str:
        """Human readable representation."""
        return f"<muffin.Plugin: { self.name }>"

    @property
    def app(self) -> Application:
        """Get the application."""
        if self.__app__ is None:
            raise PluginNotInstalledError()

        return self.__app__

    def setup(self, app: Application, *, name: Optional[str] = None, **options):
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
            return

        app.plugins[self.name] = self
        self.__app__ = app

        # Register a middleware
        if self.middleware:
            app.middleware(to_awaitable(self.middleware))

        # Bind startup
        if self.startup:
            app.on_startup(self.startup)

        # Bind shutdown
        if self.shutdown:
            app.on_shutdown(self.shutdown)
