""" Implement Muffin Application. """
import asyncio
import logging
import os
from importlib import import_module

import ujson as json
from aiohttp import web
from cached_property import cached_property


CONFIGURATION_ENVIRON_VARIABLE = 'MUFFIN_CONFIG'


class MuffinException(Exception):

    """ Implement a Muffin's exception. """

    pass


class Plugins(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class Application(web.Application):

    """ Do some stuff. """

    # Default application settings
    __defaults = {

        # Install the plugins
        'PLUGINS': (
            'muffin.plugins.manage:ManagePlugin',
            'muffin.plugins.jade:JadePlugin',
            'muffin.plugins.peewee:PeeweePlugin',
            'muffin.plugins.session:SessionPlugin',
        ),

        # Configuration module
        'CONFIG': 'config',

        # Enable debug mode
        'DEBUG': False
    }

    def __init__(self, name, *, loop=None, router=None, middlewares=(), logger=web.web_logger,
                 handler_factory=web.RequestHandlerFactory, **OPTIONS):
        """ Initialize the application. """
        super().__init__(loop=loop, router=router, middlewares=middlewares, logger=logger,
                         handler_factory=handler_factory)

        self.name = name
        self.defaults = dict(self.__defaults)
        self.defaults.update(OPTIONS)

        self._middlewares = list(self._middlewares)

        # Setup logging
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            '[%Y-%m-%d %H:%M:%S %z]'))
        self.logger.addHandler(ch)
        self.logger.setLevel('DEBUG') if self.config['DEBUG'] else self.logger.setLevel('WARNING')

        self.plugins = Plugins()
        for plugin in self.config['PLUGINS']:
            try:
                self.install(plugin)
            except Exception as exc:
                self.logger.error('Plugin is invalid: %s (%s)' % (plugin, exc))

    @cached_property
    def config(self):
        """ Load the application configuration. """
        config = dict(self.defaults)
        module = os.environ.get(CONFIGURATION_ENVIRON_VARIABLE, config['CONFIG'])
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

        if hasattr(plugin, 'middleware_factory'):
            self.middlewares.append(plugin.middleware_factory)

        self.plugins[plugin.name] = plugin

    def view(self, path, method='GET', name=None):
        """ Convert a view to couroutine and bind a route. """
        def wrapper(view):
            if not asyncio.iscoroutinefunction(view):
                view = asyncio.coroutine(view)

            def wrap_response(request, **kwargs):
                response = yield from view(request, **kwargs)

                if isinstance(response, (list, dict)):
                    response = web.Response(text=json.dumps(response),
                                            content_type='application/json')

                elif not isinstance(response, web.Response):
                    response = web.Response(text=str(response), content_type='text/html')

                self.logger.info('%s %d %s', request.method, response.status, request.path)
                return response

            self.router.add_route(method, path, wrap_response, name=name)

        return wrapper
