""" Implement Muffin Application. """
import asyncio
import logging
import re
import os
from importlib import import_module
from types import FunctionType

from aiohttp import web
from cached_property import cached_property

from .handler import Handler
from .utils import Structure


CONFIGURATION_ENVIRON_VARIABLE = 'MUFFIN_CONFIG'
RETYPE = type(re.compile('@'))


class MuffinException(Exception):

    """ Implement a Muffin's exception. """

    pass


class RawRoute(web.DynamicRoute):

    def url(self, *, parts, query=None):
        return None


# FIXME: See https://github.com/KeepSafe/aiohttp/pull/291
class Router(web.UrlDispatcher):

    """ Support raw regexps in path. """

    def add_route(self, method, path, handler, *, name=None):
        assert callable(handler), handler
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)
        method = method.upper()
        assert method in self.METHODS, method

        if isinstance(path, RETYPE):
            route = RawRoute(method, handler, name, path, path.pattern)
            self._register_endpoint(route)
            return route

        return super(Router, self).add_route(method, path, handler, name=name)


class Application(web.Application):

    """ Improve aiohttp Application. """

    # Default application settings
    __defaults = {

        # Configuration module
        'CONFIG': 'config',

        # Enable debug mode
        'DEBUG': False,

        # Install the plugins
        'PLUGINS': (
            'muffin.plugins.manage:ManagePlugin',
            'muffin.plugins.jade:JadePlugin',
            'muffin.plugins.peewee:PeeweePlugin',
            'muffin.plugins.session:SessionPlugin',
        ),

        # Setup static files in development
        'STATIC_PREFIX': '/static',
        'STATIC_ROOT': 'static',
    }

    def __init__(self, name, *, loop=None, router=None, middlewares=(), logger=web.web_logger,
                 handler_factory=web.RequestHandlerFactory, **OPTIONS):
        """ Initialize the application. """
        router = router or Router()

        super(Application, self).__init__(loop=loop, router=router, middlewares=middlewares,
                                          logger=logger, handler_factory=handler_factory)

        self.name = name
        self.defaults = dict(self.__defaults)
        self.defaults.update(OPTIONS)

        self._middlewares = list(self._middlewares)
        self._start_callbacks = []

        # Setup logging
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            '[%Y-%m-%d %H:%M:%S %z]'))
        self.logger.addHandler(ch)
        self.logger.setLevel('DEBUG') if self.cfg.DEBUG else self.logger.setLevel('WARNING')
        self.logger.name = 'muffin'

        # Setup plugins
        self.plugins = self.ps = Structure()
        for plugin in self.cfg.PLUGINS:
            try:
                self.install(plugin)
            except Exception as exc:
                self.logger.error('Plugin is invalid: %s (%s)' % (plugin, exc))

        # Setup static files (development)
        if os.path.isdir(self.cfg.STATIC_ROOT):
            self.router.add_static(self.cfg.STATIC_PREFIX, self.cfg.STATIC_ROOT)
        else:
            self.logger.warn('Disable STATIC_ROOT (hasnt found): %s' % self.cfg.STATIC_ROOT)

    def __call__(self, *args, **kwargs):
        return self

    @cached_property
    def cfg(self):
        """ Load the application configuration. """
        config = Structure(self.defaults)
        module = config['CONFIG'] = os.environ.get(
            CONFIGURATION_ENVIRON_VARIABLE, config['CONFIG'])
        try:
            module = import_module(module)
            config.update({
                name: getattr(module, name) for name in dir(module)
                if name == name.upper() and not name.startswith('_')
            })
        except ImportError:
            self.logger.warn("The configuration hasn't found: %s" % module)

        return config

    def install(self, plugin):
        """ Install plugin to the application. """

        if isinstance(plugin, str):
            module, attr = plugin.split(':')
            module = import_module(module)
            plugin = getattr(module, attr)

        if isinstance(plugin, type):
            plugin = plugin()

        if hasattr(plugin, 'setup'):
            plugin.setup(self)

        if hasattr(plugin, 'middleware_factory') \
                and plugin.middleware_factory not in self.middlewares:
            self.middlewares.append(plugin.middleware_factory)

        if hasattr(plugin, 'start'):
            self.register_on_start(plugin.start)

        self.plugins[plugin.name] = plugin

    @asyncio.coroutine
    def start(self):
        """ Start application. """
        for (cb, args, kwargs) in self._start_callbacks:
            try:
                res = cb(self, *args, **kwargs)
                if (asyncio.iscoroutine(res) or isinstance(res, asyncio.Future)):
                    yield from res
            except Exception as exc:
                self._loop.call_exception_handler({
                    'message': "Error in start callback",
                    'exception': exc,
                    'application': self,
                })

    def register_on_start(self, func, *args, **kwargs):
        self._start_callbacks.append((func, args, kwargs))

    def register(self, *paths, methods=['GET'], name=None):
        """ Register function (coroutine) or muffin.Handler to application and bind to route. """

        if isinstance(methods, str):
            methods = [methods]

        def wrapper(view):
            handler = view

            if isinstance(handler, FunctionType):
                handler = Handler.from_view(handler, *methods, name=name)

            handler.connect(self, *paths, name=name)

            return view

        return wrapper


def run():
    """ Run the Gunicorn Application. """
    from .worker import GunicornApp

    GunicornApp("%(prog)s [OPTIONS] [APP]").run()


if __name__ == '__main__':
    run()
