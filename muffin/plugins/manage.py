import argparse
import inspect
import sys


class ManagePlugin(object):

    name = 'manage'

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Manage Muffin Application")
        self.parsers = self.parser.add_subparsers(dest='subparser')
        self.handlers = dict()

    def setup(self, app):

        self.app = app

        app.config.setdefault('MANAGE_SHELL', {'app': app})

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
            app.run(port=port)

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
