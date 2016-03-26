"""CLI Support is here."""
import argparse
import asyncio
import inspect
import logging
import multiprocessing
import os
import re
import sys
from shutil import copy

from muffin import CONFIGURATION_ENVIRON_VARIABLE, __version__
from muffin.utils import MuffinException


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
            ctx = {'app': app}
            return ctx

        app.cfg.setdefault('MANAGE_SHELL', shell_ctx)

        @self.command
        def shell(ipython: bool=True):
            """Run the application shell.

            :param ipython: Use IPython as shell
            """
            app.loop.run_until_complete(app.start())

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
                    sh(global_ns={}, local_ns=namespace)
                    return

            from code import interact
            interact(banner, local=namespace)

            app.loop.run_until_complete(app.finish())

        workers = 1
        if not app.cfg.DEBUG:
            workers = multiprocessing.cpu_count()

        @self.command
        def run(bind: str='127.0.0.1:5000', daemon: bool=False, pid: str=None,
                reload: bool=self.app.cfg.DEBUG, timeout: int=30, name: str=self.app.name,
                worker_class: str='muffin.worker.GunicornWorker', workers: int=workers,
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
            from muffin.worker import GunicornApp

            gapp = GunicornApp(
                usage="%(prog)s run [OPTIONS]", config=self.app.cfg.CONFIG)
            gapp.app_uri = app
            gapp.cfg.set('bind', bind)
            gapp.cfg.set('daemon', daemon)
            gapp.cfg.set('pidfile', pid)
            gapp.cfg.set('proc_name', name)
            gapp.cfg.set('reload', reload)
            gapp.cfg.set('timeout', timeout)
            gapp.cfg.set('worker_class', worker_class)
            if workers:
                gapp.cfg.set('workers', workers)

            if log_file:
                gapp.cfg.set('errorlog', log_file)
            if access_logfile:
                gapp.cfg.set('accesslog', access_logfile)
            gapp.run()

        @self.command
        def collect(destination: str, source: list=app.cfg.STATIC_FOLDERS,
                    replace=False, symlink=True):
            """Collect static files from the application and plugins.

            :param destination: Path where static files will be collected.
            :param replace: Replace existed files
            :param source: Sources from static files will be copied
            :param symlink: Create symlinks except file copy

            """
            sources = dict()
            for path in source:
                path = os.path.abspath(path)
                for root, _, files in os.walk(path):
                    for f in files:
                        fpath = os.path.join(root, f)
                        rpath = os.path.relpath(fpath, path)
                        if rpath in sources:
                            app.logger.info('Already collected: %s' % fpath)
                            continue
                        sources[rpath] = fpath

            destination = os.path.abspath(destination)
            if not os.path.exists(destination):
                raise MuffinException('Destination is not exist: %s' % destination)

            for rpath, fpath in sources.items():
                dpath = os.path.join(destination, rpath)
                if fpath == dpath:
                    continue

                if os.path.exists(dpath):
                    if not replace or os.path.getmtime(dpath) >= os.path.getmtime(fpath):
                        continue
                    os.remove(dpath)
                ddir = os.path.dirname(dpath)
                if not os.path.exists(ddir):
                    os.makedirs(ddir)

                if symlink:
                    os.symlink(fpath, dpath)
                    app.logger.info('Linked: %s' % rpath)

                else:
                    copy(fpath, dpath)
                    app.logger.info('Copied: %s' % rpath)

    def command(self, func):
        """Define CLI command."""
        header = '\n'.join([s for s in (func.__doc__ or '').split('\n')
                            if not s.strip().startswith(':')])
        parser = self.parsers.add_parser(func.__name__, description=header)
        args, vargs, kw, defs, kwargs, kwdefs, anns = inspect.getfullargspec(func)
        defs = defs or []
        kwargs_ = dict(zip(args[-len(defs):], defs))
        docs = dict(PARAM_RE.findall(func.__doc__ or ""))

        for name in args:
            argname = name.replace('_', '-').lower()
            arghelp = docs.get(name, '')

            if name not in kwargs_:
                parser.add_argument(argname, help=arghelp)
                continue

            value = kwargs_[name]

            if isinstance(value, bool):
                if value:
                    parser.add_argument("--no-" + argname, dest=name, action="store_false",
                                        help="Disable %s" % (arghelp or name).lower())
                else:
                    parser.add_argument("--" + argname, dest=name, action="store_true",
                                        help="Enable %s" % (arghelp or name).lower())
                continue

            if isinstance(value, list):
                parser.add_argument("--" + argname, action="append",
                                    default=value, help=arghelp)
                continue

            parser.add_argument("--" + argname, type=anns.get(name, type(value)),
                                default=value, help=arghelp + ' [%s]' % repr(value))

        self.handlers[func.__name__] = func
        func.parser = parser
        return func

    def shell(self, func):
        """Set shell context function."""
        self.app.cfg.MANAGE_SHELL = func

    def __call__(self, *args, prog=False):
        """Parse arguments and run handler."""
        if prog:
            self.parser.prog = prog
        if not args:
            args = sys.argv[1:]
        args_, _ = self.parser.parse_known_args(args)
        kwargs = dict(args_._get_kwargs())

        handler = self.handlers.get(kwargs.pop('subparser'))
        if not handler:
            self.parser.print_help()
            sys.exit(1)

        try:
            res = handler(**kwargs)
            if asyncio.iscoroutine(res):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(res)

            sys.exit(0)
        except Exception as e:
            sys.exit(e)


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
        app.logger.info('Application is loaded: %s' % app.name)
    except Exception as exc:
        logging.exception(exc)
        raise sys.exit(1)

    app.manage(*subargs_, prog='muffin %s' % args_.app)

# pylama:ignore=C901,W0612,W0703,W0212
