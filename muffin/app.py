"""Implement Muffin Application."""
import logging.config
import os
from importlib import import_module
from inspect import isfunction, isclass, ismethod
import types

from aiohttp import web, log
from aiohttp.hdrs import METH_ANY
from cached_property import cached_property

from . import CONFIGURATION_ENVIRON_VARIABLE
from .handler import Handler
from .manage import Manager
from .utils import LStruct, to_coroutine
from .urls import SafeStaticResource


class MuffinException(Exception):

    """Exception class for Muffin errors."""

    pass


class BaseApplication(web.Application):

    def register(self, *paths, methods=None, name=None, handler=None):
        """Register function/coroutine/muffin.Handler with the application.

        Usage example:

        .. code-block:: python

            @app.register('/hello')
            def hello(request):
                return 'Hello World!'


        """
        if isinstance(methods, str):
            methods = [methods]

        def wrapper(view):
            if handler is None:

                handler_ = view
                methods_ = methods or [METH_ANY]

                if isfunction(handler_) or ismethod(handler_):
                    handler_ = Handler.from_view(view, *methods_, name=name)

                handler_.bind(self, *paths, methods=methods_, name=name)

            else:

                view_name = view.__name__
                if not hasattr(handler, view_name):
                    setattr(handler, view_name, to_coroutine(view))
                name_ = name or view_name
                handler.bind(self, *paths, methods=methods, name=name_, view=view_name)

            return view

        # Support for @app.register(func)
        if len(paths) == 1 and callable(paths[0]):
            view = paths[0]

            if isclass(view) and issubclass(view, BaseException):
                return wrapper

            paths = []
            return wrapper(view)

        return wrapper


class Application(BaseApplication):

    """Upgrade Aiohttp Application."""

    # Default application options
    defaults = {

        # Path to configuration module
        'CONFIG': None,

        # Enable debug mode (optional)
        'DEBUG': ...,

        # Plugins to install
        'PLUGINS': [],

        # Logging options
        'ACCESS_LOG': '-',  # File path to access log, - to stderr
        'ACCESS_LOG_FORMAT': '%a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i"',
        'LOG_LEVEL': 'WARNING',
        'LOG_FORMAT': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        'LOG_DATE_FORMAT': '[%Y-%m-%d %H:%M:%S]',

        # Setup static files in development
        'STATIC_PREFIX': '/static',
        'STATIC_FOLDERS': [],
    }

    uri = None

    def __init__(self, name, *, logger=log.web_logger, middlewares=(), handler_args=None,
                 client_max_size=1024**2, debug=..., **OPTIONS):
        """Initialize the application."""
        super(Application, self).__init__(
            logger=logger, middlewares=middlewares, handler_args=handler_args,
            client_max_size=client_max_size, debug=debug)

        self.name = name

        # Overide options
        self.defaults['CONFIG'] = OPTIONS.pop('CONFIG', self.defaults['CONFIG'])
        self.cfg.update(OPTIONS)
        if self.cfg.DEBUG is not ...:
            self._debug = self.cfg.DEBUG

        # Setup logging
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(self.cfg.LOG_FORMAT, self.cfg.LOG_DATE_FORMAT))
            self.logger.addHandler(ch)
            self.logger.setLevel(self.cfg.LOG_LEVEL)
            self.logger.propagate = False

        LOGGING_CFG = self.cfg.get('LOGGING')
        if LOGGING_CFG and isinstance(LOGGING_CFG, dict):
            logging.config.dictConfig(LOGGING_CFG)

        # Setup CLI
        self.manage = Manager(self)

        self._error_handlers = {}

        # Setup static files
        if isinstance(self.cfg.STATIC_FOLDERS, str):
            self.cfg.STATIC_FOLDERS = [self.cfg.STATIC_FOLDERS]

        elif not isinstance(self.cfg.STATIC_FOLDERS, list):
            self.cfg.STATIC_FOLDERS = list(self.cfg.STATIC_FOLDERS)

        # Setup plugins
        self.plugins = self.ps = LStruct()
        for plugin in self.cfg.PLUGINS:
            try:
                self.install(plugin)
            except Exception as exc:  # noqa
                self.logger.error('Plugin is invalid: %s', plugin)
                self.logger.exception(exc)

    def __repr__(self):
        """Human readable representation."""
        return "<Application: %s>" % self.name

    @cached_property
    def cfg(self):
        """Load the application configuration.

        This method loads configuration from python module.
        """
        config = LStruct(self.defaults)
        module = config['CONFIG'] = os.environ.get(
            CONFIGURATION_ENVIRON_VARIABLE, config['CONFIG'])

        if module:
            try:
                module = import_module(module)
                config.update({
                    name: getattr(module, name) for name in dir(module)
                    if name == name.upper() and not name.startswith('_')
                })

            except ImportError as exc:
                config.CONFIG = None
                message = "Error importing %s: %s" % (module, exc)
                self.register_on_start(lambda app: app.logger.error(message))

        return config

    def install(self, plugin, name=None, **opts):
        """Install plugin to the application."""
        source = plugin

        if isinstance(plugin, str):
            module, _, attr = plugin.partition(':')
            module = import_module(module)
            plugin = getattr(module, attr or 'Plugin', None)

        if isinstance(plugin, types.ModuleType):
            plugin = getattr(module, 'Plugin', None)

        if plugin is None:
            raise MuffinException('Plugin is not found %r' % source)

        name = name or plugin.name
        if name in self.ps:
            raise MuffinException('Plugin with name `%s` is already intalled.' % name)

        if isinstance(plugin, type):
            plugin = plugin(**opts)

        if hasattr(plugin, 'setup'):
            plugin.setup(self)

        if hasattr(plugin, 'middleware') and plugin.middleware not in self.middlewares:
            self.middlewares.append(plugin.middleware)

        if hasattr(plugin, 'startup'):
            self.on_startup.append(plugin.startup)

        if hasattr(plugin, 'cleanup'):
            self.on_cleanup.append(plugin.cleanup)

        # Save plugin links
        self.ps[name] = plugin

        return plugin

    async def startup(self):
        """Start the application.

        Support for start-callbacks and lock the application's configuration and plugins.
        """
        if self.frozen:
            return False

        if self._error_handlers:
            self.middlewares.append(_exc_middleware_factory(self))

        # Register static paths
        for path in self.cfg.STATIC_FOLDERS:
            self.router.register_resource(SafeStaticResource(self.cfg.STATIC_PREFIX, path))

        await super(Application, self).startup()

    def pre_freeze(self) -> None:
        # Lock the application's settings and plugin's registry after start
        self.cfg.freeze()
        self.ps.freeze()

        # Freeze plugin's
        for plugin in self.ps.values():
            plugin.freeze()

        return super(Application, self).pre_freeze()


def _exc_middleware_factory(app):
    """Handle exceptions.

    Route exceptions to handlers if they are registered in application.
    """

    @web.middleware
    async def middleware(request, handler):
        try:
            return await handler(request)
        except Exception as exc:
            for cls in type(exc).mro():
                if cls in app._error_handlers:
                    request.exception = exc
                    response = await app._error_handlers[cls](request)
                    return response
            raise

    return middleware


def run():
    """Run Gunicorn Application."""
    from .worker import GunicornApp

    GunicornApp("%(prog)s [OPTIONS] [APP]").run()


if __name__ == '__main__':
    run()

#  pylama:ignore=W0212,W1504
