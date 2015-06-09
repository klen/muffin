import argparse
import inspect
import os
import re
import sys
from shutil import copy

from muffin import CONFIGURATION_ENVIRON_VARIABLE
from muffin.utils import MuffinException


PARAM_RE = re.compile('^\s+:param (\w+): (.+)$', re.M)


class Manager(object):

    """ Support application commands. """

    def __init__(self, app):
        self.app = app
        self.parser = argparse.ArgumentParser(description="Manage %s" % app.name.capitalize())
        self.parser.add_argument('app', metavar='app', type=str, help='Path to application.')
        self.parser.add_argument('--config', type=str, help='Path to configuration.')
        self.parsers = self.parser.add_subparsers(dest='subparser')
        self.handlers = dict()

        def shell_ctx():
            ctx = {'app': app}
            return ctx

        app.cfg.setdefault('MANAGE_SHELL', shell_ctx)

        @self.command
        def shell(ipython:bool=True):
            """ Run the application shell.

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

        @self.command
        def run(timeout:int=30, reload:bool=self.app.cfg.DEBUG, name:str=self.app.name,
                pid:str=None, workers:int=1, bind:str='127.0.0.1:5000', log_file:str=None,
                worker_class:str='muffin.worker.GunicornWorker', daemon:bool=False):
            """ Run the application.

            :param bind: The socket to bind
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
                usage="%(prog)s APP_MODULE run [OPTIONS]", config=self.app.cfg.CONFIG)
            gapp.app_uri = app
            gapp.cfg.set('bind', bind)
            gapp.cfg.set('pidfile', pid)
            gapp.cfg.set('proc_name', name)
            gapp.cfg.set('reload', reload)
            gapp.cfg.set('daemon', daemon)
            gapp.cfg.set('timeout', timeout)
            gapp.cfg.set('worker_class', worker_class)
            if log_file:
                gapp.cfg.set('errorlog', log_file)
            gapp.run()

        @self.command
        def collect(destination:str, replace=False, symlink=True):
            """ Collect static files from the application and plugins.

            :param destination: Path where static files will be collected.
            :param replace: Replace existed files
            :param symlink: Create symlinks except file copy

            """
            sources = dict()
            for path in app.cfg.STATIC_FOLDERS:
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
                parser.add_argument("--" + argname, dest=name, action="store_true",
                                    help="Enable %s" % (arghelp or name).lower())
                parser.add_argument("--no-" + argname, dest=name, action="store_false",
                                    help="Disable %s" % (arghelp or name).lower())
                continue

            if isinstance(value, list):
                parser.add_argument("--" + argname, action="append",
                                    default=value, help=arghelp)
                continue

            parser.add_argument("--" + argname, type=anns.get(name, type(value)),
                                default=value, help=arghelp + ' [%s]' % value)

        self.handlers[func.__name__] = func
        func.parser = parser
        return func

    def shell(self, func):
        self.app.cfg.MANAGE_SHELL = func

    def __call__(self, args=None):
        """ Parse arguments and run handler. """
        args_, unknown = self.parser.parse_known_args(args)
        kwargs = dict(args_._get_kwargs())

        handler = self.handlers.get(kwargs.pop('subparser'))
        if not handler:
            self.parser.print_help()
            sys.exit(1)

        actions = [a.dest for a in handler.parser._actions]
        for name in ('app', 'config'):
            if name not in actions:
                kwargs.pop(name, None)

        try:
            handler(**kwargs)
            sys.exit(0)
        except Exception as e:
            sys.exit(e)


def run():
    """ CLI endpoint. """
    sys.path.insert(0, os.getcwd())

    parser = argparse.ArgumentParser(description="Manage Application")
    parser.add_argument('app', metavar='app', type=str, help='Path to application.')
    parser.add_argument('--config', type=str, help='Path to configuration.')

    args_ = [_ for _ in sys.argv[1:] if _ not in ["--help", "-h"]]
    args_, unknown = parser.parse_known_args(args_)
    if args_.config:
        os.environ[CONFIGURATION_ENVIRON_VARIABLE] = args_.config

    from gunicorn.util import import_app

    try:
        app_uri = args_.app
        if ':' not in app_uri:
            app_uri += ':app'
        app = import_app(app_uri)
        app.logger.info('Application is loaded: %s' % app.name)

    except Exception as e:
        print(e)
        raise sys.exit(1)

    app.manage()

# pylama:ignore=C901
