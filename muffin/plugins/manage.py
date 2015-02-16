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

        app.config.setdefault('MANAGE_SHELL', {'app': app})
        self.parser.description = "Manage %s" % app.name.capitalize()

        @self.command
        def shell():
            """ Run the application shell. """
            from werkzeug import script

            ctx = app.config['MANAGE_SHELL']
            if callable(ctx):
                ctx = ctx()

            return script.make_shell(lambda: ctx, "Loaded objects: " + ", ".join(ctx.keys()))()

        @self.command
        def runserver(port=5000):
            """ Run the application. """
            from muffin.worker import GunicornApp
            gapp = GunicornApp(app, {'bind': '127.0.0.1:%d' % port})
            gapp.run()

    def command(self, func):
        parser = self.parsers.add_parser(func.__name__, description=func.__doc__)
        args, varargs, keywords, defaults = inspect.getargspec(func)
        if args:
            for name, value in zip(args, defaults):
                argname = "--%s" % name
                if isinstance(value, bool):
                    parser.add_argument(argname, action="store_%s" % str(not value).lower())
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
