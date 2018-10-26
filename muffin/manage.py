"""CLI Support is here."""
import argparse
import asyncio
import inspect
import logging
import multiprocessing
import os
import re
import sys

from muffin import CONFIGURATION_ENVIRON_VARIABLE, __version__


PARAM_RE = re.compile(r'^\s+:param (\w+): (.+)$', re.M)


class Manager(object):

    """Provide simple interface to make application's commands.

    ::

        @app.manage.command
        def hello(name, upper=False):
            '''Say hello!

            :param name: an user name
            :param upper: to upper string

            '''
            message = 'Hello %s!' % name
            if upper:
                message = message.upper()
            print(message)

    ::

        $ muffin app hello Mike
        Hello Mike!

        $ muffin app hello Mike --upper
        HELLO MIKE!

    """

    def __init__(self, app):
        """Initialize the commands."""
        self.app = app
        self.parser = argparse.ArgumentParser(description="Manage %s" % app.name.capitalize())
        self.parsers = self.parser.add_subparsers(dest='subparser')
        self.handlers = dict()

        def shell_ctx():
            return {'app': app, 'run': lambda coro: app.loop.run_until_complete(coro)}

        app.cfg.setdefault('MANAGE_SHELL', shell_ctx)

        @self.command
        def shell(ipython: bool=True):
            """Run the application shell.

            :param ipython: Use IPython as shell
            """
            banner = '\nInteractive Muffin Shell\n'
            namespace = app.cfg.MANAGE_SHELL
            if callable(namespace):
                namespace = namespace()
            banner += "Loaded objects: %s" % list(namespace.keys())
            if ipython:
                try:
                    from IPython.terminal.embed import InteractiveShellEmbed
                    sh = InteractiveShellEmbed(banner1=banner)
                except ImportError:
                    pass
                else:
                    sh(local_ns=namespace)
                    return

            from code import interact
            interact(banner, local=namespace)

        workers = 1
        debug = app.cfg.DEBUG is not ... and app.cfg.DEBUG
        if not debug:
            workers = multiprocessing.cpu_count()

        @self.command(init=False)
        def run(bind: str='127.0.0.1:5000', daemon: bool=False, pid: str=None,
                reload: bool=debug, timeout: int=30, name: str=self.app.name,
                worker_class: str='aiohttp.worker.GunicornWebWorker', workers: int=workers,
                log_file: str=None, access_logfile: str=self.app.cfg.ACCESS_LOG):
            """Run the application.

            :param bind: The socket to bind
            :param daemon: Daemonize the program
            :param log_file: The Error log file to write to
            :param name: A base to use with setproctitle for process naming
            :param pid: A filename to use for the PID file
            :param reload: Restart workers when code changes
            :param timeout: Workers silent for more than this many seconds are killed and restarted
            :param worker_class: The type of workers to use.
            :param workers: The number of worker processes for handling requests

            """
            from gunicorn.app.base import Application
            from gunicorn.util import import_app

            class MuffinServer(Application):

                def init(self, *args):
                    """Store config in env."""
                    os.environ[CONFIGURATION_ENVIRON_VARIABLE] = app.cfg.CONFIG or ''

                def load(self):
                    """Reload modules."""
                    if not app.uri:
                        return app

                    module, *_ = app.uri.split(':', 1)
                    if module in sys.modules:
                        sys.modules.pop(module)
                        paths = [p for p in sys.modules if p.startswith('%s.' % module)]
                        for path in paths:
                            sys.modules.pop(path)
                    return import_app(app.uri)

            server = MuffinServer('%(prog)s run [OPTIONS]')
            server.cfg.set('bind', bind)
            server.cfg.set('daemon', daemon)
            server.cfg.set('pidfile', pid)
            server.cfg.set('proc_name', name)
            server.cfg.set('reload', reload)
            server.cfg.set('timeout', timeout)
            server.cfg.set('worker_class', worker_class)
            if workers:
                server.cfg.set('workers', workers)

            if log_file:
                server.cfg.set('errorlog', log_file)
            if access_logfile:
                server.cfg.set('accesslog', access_logfile)

            server.run()

    def command(self, init=False):
        """Define CLI command."""

        def wrapper(func):
            header = '\n'.join([s for s in (func.__doc__ or '').split('\n')
                                if not s.strip().startswith(':')])
            parser = self.parsers.add_parser(func.__name__, description=header)
            args, vargs, kw, defs, kwargs, kwdefs, anns = inspect.getfullargspec(func)
            defs = defs or []
            kwargs_ = dict(zip(args[-len(defs):], defs))
            docs = dict(PARAM_RE.findall(func.__doc__ or ""))

            def process_arg(name, *, value=..., **opts):
                argname = name.replace('_', '-').lower()
                arghelp = docs.get(vargs, '')
                if value is ...:
                    return parser.add_argument(argname, help=arghelp, **opts)

                if isinstance(value, bool):
                    if value:
                        return parser.add_argument(
                            "--no-" + argname, dest=name, action="store_false",
                            help="Disable %s" % (arghelp or name).lower())

                    return parser.add_argument(
                        "--" + argname, dest=name, action="store_true",
                        help="Enable %s" % (arghelp or name).lower())

                if isinstance(value, list):
                    return parser.add_argument(
                        "--" + argname, action="append", default=value, help=arghelp)

                return parser.add_argument(
                    "--" + argname, type=anns.get(name, type(value)),
                    default=value, help=arghelp + ' [%s]' % repr(value))

            if vargs:
                process_arg('*', nargs="*", metavar=vargs)

            for name, value in (kwdefs or {}).items():
                process_arg(name, value=value)

            for name in args:
                process_arg(name, value=kwargs_.get(name, ...))

            self.handlers[func.__name__] = func
            func.parser = parser
            return func

        if callable(init):
            init.__init__ = True
            return wrapper(init)

        def decorator(func):
            func.__init__ = bool(init)
            return wrapper(func)

        return decorator

    def shell(self, func):
        """Set shell context function."""
        self.app.cfg.MANAGE_SHELL = func

    def __call__(self, *args, prog=False):
        """Parse arguments and run handler."""
        if prog:
            self.parser.prog = prog
        if not args:
            args = sys.argv[1:]

        ns, _ = self.parser.parse_known_args(args)
        kwargs = dict(ns._get_kwargs())

        handler = self.handlers.get(kwargs.pop('subparser'))
        if not handler:
            self.parser.print_help()
            sys.exit(1)

        loop = asyncio.get_event_loop()
        self.app._set_loop(loop)

        if handler.__init__:
            self.app.on_startup.freeze()
            loop.run_until_complete(self.app.startup())
            self.app.freeze()

        args = kwargs.pop('*', [])

        try:

            res = handler(*args, **kwargs)
            if asyncio.iscoroutine(res):
                loop.run_until_complete(res)

            sys.exit(0)

        except Exception as e:
            sys.exit(e)

        finally:
            if not loop.is_closed() and handler.__init__:
                loop.run_until_complete(self.app.cleanup())
                loop.run_until_complete(self.app.shutdown())


def run():
    """CLI endpoint."""
    sys.path.insert(0, os.getcwd())
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

    parser = argparse.ArgumentParser(description="Manage Application", add_help=False)
    parser.add_argument('app', metavar='app',
                        type=str, help='Application module path')
    parser.add_argument('--config', type=str, help='Path to configuration.')
    parser.add_argument('--version', action="version", version=__version__)

    args_, subargs_ = parser.parse_known_args(sys.argv[1:])
    if args_.config:
        os.environ[CONFIGURATION_ENVIRON_VARIABLE] = args_.config

    from gunicorn.util import import_app

    app_uri = args_.app
    if ':' not in app_uri:
        app_uri += ':app'
    try:
        app = import_app(app_uri)
        app.uri = app_uri
        app.logger.info('Application is loaded: %s' % app.name)
    except Exception as exc:
        logging.exception(exc)
        raise sys.exit(1)

    app.manage(*subargs_, prog='muffin %s' % args_.app)

# pylama:ignore=C901,W0612,W0703,W0212
