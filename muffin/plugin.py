"""A helper to write Muffin Plugins."""

import typing as t
from abc import ABC, abstractmethod

from asgi_tools.utils import to_awaitable
from modconfig import Config

from . import MuffinException
from .app import Application


class PluginException(MuffinException):

    """Implement any exception in plugins."""


class BasePlugin(ABC):

    """Base class for Muffin plugins."""

    # Plugin options with default values
    defaults: t.Dict[str, t.Any] = {}
    middleware: t.Optional[t.Callable] = None
    startup: t.Optional[t.Callable] = None
    shutdown: t.Optional[t.Callable] = None

    @property
    @abstractmethod
    def name(self):
        """Plugin has to have a name."""
        raise NotImplementedError

    def __init__(self, app: Application = None, **options):
        """Save application and create he plugin's configuration."""
        self.cfg = Config(prefix="%s_" % self.name.upper(), update_from_env=False, **self.defaults)
        self.cfg.update(**options)

        if app is not None:
            self.setup(app)

    def setup(self, app: Application, **options):
        """Bind app and update the plugin's configuration."""
        self.app = app
        self.app.plugins[self.name] = self

        # Update configuration
        self.cfg.update_from_dict(dict(app.cfg), prefix=self.cfg.prefix, exist_only=True)
        self.cfg.update_from_dict(options)

        # Bind middleware
        if self.middleware:
            self.app.middleware(to_awaitable(self.middleware))

        # Bind startup
        if self.startup:
            self.app.on_startup(self.startup)

        # Bind shutdown
        if self.shutdown:
            self.app.on_shutdown(self.shutdown)

    async def conftest(self):
        """Configure tests."""
        pass
