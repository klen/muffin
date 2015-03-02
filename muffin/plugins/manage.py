import argparse
import inspect
import sys

from . import BasePlugin


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

        app.config.setdefault('MANAGE_SHELL', shell_ctx)
        self.parser.description = "Manage %s" % app.name.capitalize()

        @self.command
        def shell(ipython=True):
            """ Run the application shell. """
            banner = '\nInteractive Muffin Shell\n'
            namespace = app.config['MANAGE_SHELL']
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
        def runserver(host='127.0.0.1', port=5000, reload=True):
            """ Run the application. """
            from muffin.worker import GunicornApp
            gapp = GunicornApp(usage="%(prog)s [OPTIONS] [APP_MODULE]",
                               config=app.config['CONFIG'])
            gapp.app_uri = app
            gapp.cfg.set('bind', '%s:%s' % (host, port))
            gapp.cfg.set('reload', reload)
            gapp.run()

    def command(self, func):
        parser = self.parsers.add_parser(func.__name__, description=func.__doc__)
        args, varargs, keywords, defaults = inspect.getargspec(func)
        if args and defaults:
            for name, value in zip(args, defaults):
                argname = "--%s" % name.lower()
                if isinstance(value, bool):
                    if not value:
                        parser.add_argument(argname, dest=name, action="store_true",
                                            help="Enable %s" % name)
                    else:
                        argname = "--no-%s" % name.lower()
                        parser.add_argument(argname, dest=name, action="store_false",
                                            help="Disable %s" % name)
                elif isinstance(value, list):
                    parser.add_argument(argname, action="append", default=value)
                else:
                    parser.add_argument(argname, default=value, type=type(value))
        self.handlers[func.__name__] = func
        return func

    def shell(self, func):
        self.app.config['MANAGE_SHELL'] = func

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

# pylama:ignore=E1103,W0612
