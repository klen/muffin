import argparse
import inspect
import os
import re
import sys

from muffin import CONFIGURATION_ENVIRON_VARIABLE


PARAM_RE = re.compile('^\s+:param (\w+): (.+)$', re.M)


class Manager(object):

    """ Support application commands. """

    parser = argparse.ArgumentParser(description="Manage Application")
    parser.add_argument('app', metavar='app', type=str, help='Path to application.')
    parser.add_argument('--config', type=str, help='Path to configuration.')

    def __init__(self, app):
        self.app = app
        self.parsers = self.parser.add_subparsers(dest='subparser')
        self.handlers = dict()

        def shell_ctx():
            ctx = {'app': app}
            return ctx

        app.cfg.setdefault('MANAGE_SHELL', shell_ctx)
        self.parser.description = "Manage %s" % app.name.capitalize()

        @self.command
        def shell(ipython:bool=True):
            """ Run the application shell.

            :param ipython: Use IPython as shell

            """
            app._loop.run_until_complete(app.start())

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

            app._loop.run_until_complete(app.finish())

        @self.command
        def run(timeout:int=30, reload:bool=self.app.cfg.DEBUG, config:str=self.app.cfg.CONFIG,
                name:str=self.app.name, pid:str=None, workers:int=1, bind:str='127.0.0.1:5000',
                log_file:str=None, worker_class:str='muffin.worker.GunicornWorker'):
            """ Run the application.

            :param bind: The socket to bind
            :param config: The path to a Muffin config file
            :param log_file: The Error log file to write to
            :param name: A base to use with setproctitle for process naming
            :param pid: A filename to use for the PID file
            :param reload: Restart workers when code changes
            :param timeout: Workers silent for more than this many seconds are killed and restarted
            :param worker_class: The type of workers to use.
            :param workers: The number of worker processes for handling requests

            """
            from muffin.worker import GunicornApp

            # Clean argv
            sys.argv = sys.argv[1:]

            gapp = GunicornApp(usage="%(prog)s APP_MODULE run [OPTIONS]", config=config)
            gapp.app_uri = app
            gapp.cfg.set('bind', bind)
            gapp.cfg.set('pidfile', pid)
            gapp.cfg.set('proc_name', name)
            gapp.cfg.set('reload', reload)
            gapp.cfg.set('timeout', timeout)
            gapp.cfg.set('worker_class', worker_class)
            if log_file:
                gapp.cfg.set('errorlog', log_file)
            gapp.run()

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
        args_ = self.parser.parse_args(args)
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
    args_ = [_ for _ in sys.argv[1:] if _ not in ["--help", "-h"]]
    args_, unknown = Manager.parser.parse_known_args(args_)
    if args_.config:
        os.environ[CONFIGURATION_ENVIRON_VARIABLE] = args_.config

    from gunicorn.util import import_app

    try:
        app = args_.app
        if ':' not in app:
            app += ':app'
        app = import_app(app)
    except Exception as e:
        print(e)
        raise sys.exit(1)

    app.manage()
