"""A helper to write Muffin Plugins."""

from abc import ABC, abstractmethod

from asgi_tools.utils import to_awaitable
from modconfig import Config

from . import MuffinException


class PluginException(MuffinException):

    """Implement any exception in plugins."""


class BasePlugin(ABC):

    """Base class for Muffin plugins."""

    # Plugin options with default values
    defaults = {}

    middleware = startup = shutdown = None

    @property
    @abstractmethod
    def name(self):
        """Plugin has to have a name."""
        raise NotImplementedError

    def __init__(self, app=None, **options):
        """Save application and create he plugin's configuration."""
        self.cfg = Config(prefix="%s_" % self.name.upper(),
                          update_from_env=False, ignore_case=True, **self.defaults)
        self.cfg.update(**options)

        if app is not None:
            self.init(app)

    def init(self, app, **options):
        """Bind app and update the plugin's configuration."""
        self.app = app
        self.app.plugins[self.name] = self

        # Update configuration
        self.cfg.update_from_dict(app.cfg.__dict__, prefix=self.cfg._prefix, exist_only=True)
        self.cfg.update_from_dict(options)

        # Init middleware
        if self.middleware:
            self.app.middleware(to_awaitable(self.middleware))

        # Register startup
        if self.startup:
            self.app.on_startup(self.startup)

        # Register shutdown
        if self.shutdown:
            self.app.on_shutdown(self.shutdown)

    async def conftest(self):
        """Configure tests."""
        pass
