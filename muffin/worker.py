import asyncio
import logging
import os
import sys

from gunicorn.app.base import Application as VanillaGunicornApp
from gunicorn.config import Config as VanillaGunicornConfig
from gunicorn.util import import_app
from gunicorn.workers.base import Worker as VanillaGunicornWorker

from . import CONFIGURATION_ENVIRON_VARIABLE


class GunicornApp(VanillaGunicornApp):

    """ Support Gunicorn. """

    def __init__(self, usage=None, prog=None, config=None):
        self._cfg = config
        super(GunicornApp, self).__init__(usage=usage, prog=prog)

    def init(self, parser, opts, args):
        """ Initialize the application. """
        if len(args) < 1:
            parser.error("No application module specified.")

        self.app_uri = args[0]
        self.cfg.set("default_proc_name", self.app_uri)
        logging.captureWarnings(True)

        if self.cfg.config:
            self.load_config_from_file(self.cfg.config)

    def load_default_config(self):
        """ Prepare default configuration. """
        self.cfg = VanillaGunicornConfig(self.usage, prog=self.prog)

        # Remove unused settings
        del self.cfg.settings['paste']
        del self.cfg.settings['django_settings']

        self.cfg.settings['worker_class'].default = 'muffin.worker.GunicornWorker'
        self.cfg.set('worker_class', 'muffin.worker.GunicornWorker')
        if self._cfg:
            self.cfg.set('config', self._cfg)
            os.environ[CONFIGURATION_ENVIRON_VARIABLE] = self._cfg

    def load(self):
        """ Load a Muffin application. """
        # Fix paths
        os.chdir(self.cfg.chdir)
        sys.path.insert(0, self.cfg.chdir)

        if isinstance(self.app_uri, dict):
            return self.app_uri

        return import_app(self.app_uri)


class GunicornWorker(VanillaGunicornWorker):

    """ Work with Asyncio applications. """

    def __init__(self, *args, **kwargs):
        super(GunicornWorker, self).__init__(*args, **kwargs)
        self.servers = {}

    def init_process(self):
        """ Create new event_loop after fork. """
        asyncio.get_event_loop().close()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        super().init_process()

    def run(self):
        """ Create asyncio server and start the loop. """
        container = self.app.callable
        container._loop = self.loop
        container.loop.set_debug(container.config['DEBUG'])
        handler = container.make_handler()
        for i, sock in enumerate(self.sockets):
            srv = self.loop.run_until_complete(self.loop.create_server(handler, sock=sock.sock))
            self.servers[srv] = handler

        self.notify()
        self.loop.run_forever()

    def notify(self):
        """ Call Gunicorn notify every ``self.timeout`` seconds.

        Prevent the master process from murder the worker.

        """
        super(GunicornWorker, self).notify()
        if self.alive and os.getppid() == self.ppid:
            self.loop.call_later(self.timeout, self.notify)
        else:
            self.alive = False
            self.log.info("Parent changed, shutting down: %s", self)
