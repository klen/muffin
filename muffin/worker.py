"""Gunicorn support."""
import asyncio
import logging
import os
import sys

from aiohttp.web import Application
from aiohttp.worker import GunicornWebWorker
from gunicorn.app.base import Application as VanillaGunicornApp
from gunicorn.util import import_app

from . import CONFIGURATION_ENVIRON_VARIABLE


class GunicornApp(VanillaGunicornApp):

    """Implement Gunicorn application."""

    def __init__(self, usage=None, prog=None, config=None):
        """Initialize self."""
        self._cfg = config
        super().__init__(usage=usage, prog=prog)

    def init(self, parser, opts, args):
        """Initialize the application."""
        if len(args) < 1:
            parser.error("No application module specified.")

        self.app_uri = args[0]
        self.cfg.set("default_proc_name", self.app_uri)
        logging.captureWarnings(True)

        if self.cfg.config:
            prefix = "python:"
            if os.path.exists(self.cfg.config):
                prefix = "file:"
            self.load_config_from_file(prefix + self.cfg.config)

    def load_default_config(self):
        """Prepare default configuration."""
        super().load_default_config()

        # Remove unused settings
        self.cfg.settings.pop('paste', None)

        self.cfg.settings['worker_class'].default = (
            'muffin.worker.GunicornWorker'
        )
        self.cfg.set('worker_class', 'muffin.worker.GunicornWorker')
        if self._cfg:
            self.cfg.set('config', self._cfg)
            os.environ[CONFIGURATION_ENVIRON_VARIABLE] = self._cfg

    def load_config(self):
        """Load configuration."""
        parser = self.cfg.parser()
        args, _ = parser.parse_known_args()
        self.init(parser, args, args.args)

    def load(self):
        """Load a Muffin application."""
        # Fix paths
        os.chdir(self.cfg.chdir)
        sys.path.insert(0, self.cfg.chdir)

        app = self.app_uri
        if not isinstance(app, Application):
            module, *_ = self.app_uri.split(':', 1)
            if module in sys.modules:
                sys.modules.pop(module)
                paths = [
                    p for p in sys.modules
                    if p.startswith('%s.' % module)
                ]
                for path in paths:
                    sys.modules.pop(path)
            app = import_app(app)

        return app


class GunicornWorker(GunicornWebWorker):

    """Work with Asyncio applications."""

    def run(self):
        """Create asyncio server and start the loop."""
        self.loop.set_debug(self.wsgi.cfg.DEBUG)
        self.wsgi._loop = self.loop
        self.loop.run_until_complete(self.wsgi.start())
        super().run()

    def make_handler(self, app, *args):
        """Create a handler."""
        handler = app.make_handler(
            logger=self.log, debug=app.cfg.DEBUG,
            keep_alive=self.cfg.keepalive, timeout=self.cfg.timeout,
            access_log=app.access_logger or self.log.access_log,
            access_log_format=app.cfg.ACCESS_LOG_FORMAT,
            secure_proxy_ssl_header=app.cfg.SECURE_PROXY_SSL_HEADER
        )
        return handler


class GunicornUVLoopWorker(GunicornWorker):
    """Work with asyncio application (using uvloop)"""

    def init_process(self):
        import uvloop
        asyncio.get_event_loop().close()
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        super().init_process()
