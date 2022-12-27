"""A helper to write Muffin Plugins."""

from abc import ABC
from typing import Any, Callable, Dict, Optional

from asgi_tools.utils import to_awaitable
from modconfig import Config

from muffin import MuffinException
from muffin.app import Application


class PluginException(MuffinException):
    """Implement any exception in plugins."""


class BasePlugin(ABC):
    """Base class for Muffin plugins."""

    name: str

    app: Optional[Application] = None

    # Plugin options with default values
    defaults: Dict[str, Any] = {}

    # Optional middleware method
    middleware: Optional[Callable] = None

    # Optional startup method
    startup: Optional[Callable] = None

    # Optional shutdown method
    shutdown: Optional[Callable] = None

    # Optional conftest method
    conftest: Optional[Callable] = None

    def __init__(self, app: Optional[Application] = None, **options):
        """Save application and create he plugin's configuration."""
        if getattr(self, "name", None) is None:
            raise TypeError("Plugin.name is required")

        self.cfg = Config(config_config={"update_from_env": False}, **self.defaults)

        if app is not None:
            self.setup(app, **options)
        else:
            self.cfg.update_from_dict(options, exist_only=True)

    def __repr__(self) -> str:
        """Human readable representation."""
        return f"<muffin.Plugin: { self.name }>"

    @property
    def installed(self):
        """Check the plugin is installed to an app."""
        return bool(self.app)

    def setup(self, app: Application, *, name: Optional[str] = None, **options):
        """Bind app and update the plugin's configuration."""
        # allow to redefine the name for multi plugins with same type
        self.name = name or self.name  # type: ignore
        self.app = app
        app.plugins[self.name] = self

        # Update configuration
        self.cfg.update_from_dict(
            dict(app.cfg), prefix=f"{self.name}_", exist_only=True
        )
        self.cfg.update_from_dict(options)

        # Register a middleware
        if self.middleware:
            app.middleware(to_awaitable(self.middleware))

        # Bind startup
        if self.startup:
            app.on_startup(self.startup)

        # Bind shutdown
        if self.shutdown:
            app.on_shutdown(self.shutdown)
