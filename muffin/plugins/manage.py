import argparse
import inspect
import sys
import re

from . import BasePlugin


PARAM_RE = re.compile('^\s+:param (\w+): (.+)$', re.M)


class ManagePlugin(BasePlugin):

    name = 'manage'

    def __init__(self, **options):
        super().__init__(**options)

        self.parser = argparse.ArgumentParser(description="Manage Application")
        self.parsers = self.parser.add_subparsers(dest='subparser')
        self.handlers = dict()

    def setup(self, app):

        super().setup(app)

        def shell_ctx():
            ctx = {'app': app}
            if 'peewee' in app.plugins:
                ctx['models'] = app.plugins.peewee.models
            return ctx

        app.cfg.setdefault('MANAGE_SHELL', shell_ctx)
        self.parser.description = "Manage %s" % app.name.capitalize()

        @self.command
        def shell(ipython:bool=True):
            """ Run the application shell.

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
                    sh(global_ns={}, local_ns=namespace)
                    return
            from code import interact
            interact(banner, local=namespace)

        @self.command
        def run(timeout:int=30, reload:bool=self.app.cfg.DEBUG, config:str=self.app.cfg.CONFIG,
                name:str=self.app.name, pid:str=None, workers:int=1, bind:str='127.0.0.1:5000',
                log_file:str=None):
            """ Run the application.

            :param bind: The socket to bind
            :param config: The path to a Muffin config file
            :param log_file: The Error log file to write to
            :param name: A base to use with setproctitle for process naming
            :param pid: A filename to use for the PID file
            :param reload: Restart workers when code changes
            :param timeout: Workers silent for more than this many seconds are killed and restarted
            :param workers: The number of worker processes for handling requests

            """
            from muffin.worker import GunicornApp
            gapp = GunicornApp(usage="%(prog)s [OPTIONS] [APP_MODULE]", config=config)
            gapp.app_uri = app
            gapp.cfg.set('bind', bind)
            gapp.cfg.set('pidfile', pid)
            gapp.cfg.set('proc_name', name)
            gapp.cfg.set('reload', reload)
            gapp.cfg.set('timeout', timeout)
            if log_file:
                gapp.cfg.set('errorlog', log_file)
            gapp.run()

    def command(self, func):
        header = '\n'.join([s for s in (func.__doc__ or '').split('\n')
                            if not s.strip().startswith(':')])
        parser = self.parsers.add_parser(func.__name__, description=header)
        args, vargs, kw, defs, kwargs, kwdefs, anns = inspect.getfullargspec(func)
        docs = dict(PARAM_RE.findall(func.__doc__ or ""))

        if args and defs:
            for name, value in zip(args, defs):
                argname = "--%s" % name.replace('_', '-').lower()
                _type = type(value)
                _help = docs.get(name, '')
                if anns:
                    _type = anns.get(name, _type)
                if isinstance(value, bool):
                    if not value:
                        parser.add_argument(argname, dest=name, action="store_true",
                                            help="Enable %s" % _help or name)
                    else:
                        argname = "--no-%s" % name.lower()
                        parser.add_argument(argname, dest=name, action="store_false",
                                            help="Disable %s" % _help or name)
                elif isinstance(value, list):
                    parser.add_argument(argname, action="append", default=value, help=_help)
                else:
                    parser.add_argument(argname, default=value, type=_type,
                                        help=_help + ' [%s]' % value)
        self.handlers[func.__name__] = func
        return func

    def shell(self, func):
        self.app.cfg.MANAGE_SHELL = func

    def __call__(self, args=None):
        if args is None:
            args = sys.argv[1:]
        options = self.parser.parse_args(args)
        sys.argv = sys.argv[:2]
        kwargs = dict(options._get_kwargs())
        handler = self.handlers.get(kwargs.pop('subparser'))
        if not handler:
            self.parser.print_help()
            sys.exit(1)

        try:
            handler(**kwargs)
            sys.exit(0)
        except Exception as e:
            sys.exit(e)


def manage():
    from gunicorn.util import import_app

    if len(sys.argv) < 2:
        print('Usage: muffin APPLICATION [-h] [COMMAND] [OPTIONS]')
        raise sys.exit(1)

    app_uri, *args = sys.argv[1:]
    try:
        app = import_app(app_uri)
    except Exception as e:
        print(e)
        raise sys.exit(1)

    prog = 'muffin ' + app_uri
    app.ps.manage.parser.prog = prog
    for parser in app.ps.manage.parsers.choices.values():
        parser.prog = prog + ' ' + parser.prog.split()[-1]
    app.ps.manage(args)

# pylama:ignore=E1103,W0612,E231
