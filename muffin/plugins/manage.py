import click


class ManagePlugin(object):

    name = 'manage'

    def __init__(self):
        self.cli = click.group()(lambda: None)

    def setup(self, app):

        self.app = app

        app.config.setdefault('MANAGE_SHELL', {'app': app})

        @self.command()
        def shell():
            """ Run the application shell. """
            from werkzeug import script

            ctx = app.config['MANAGE_SHELL']
            if callable(ctx):
                ctx = ctx()

            return script.make_shell(lambda: ctx, "Loaded objects: " + ", ".join(ctx.keys()))()

        @self.command()
        # @self.option('--reload/--no-reload', default=False)
        # @self.option('--debug/--no-debug', default=False)
        @self.option('--port', default=5000)
        def runserver(**kwargs):
            """ Run the application. """
            app.run(**kwargs)

    @staticmethod
    def option(*args, **kwargs):
        return click.option(*args, **kwargs)

    def command(self, *args, **kwargs):
        return self.cli.command(*args, **kwargs)

    def shell(self, func):
        self.app.config['MANAGE_SHELL'] = func

    def __call__(self, *args, **kwargs):
        return self.cli(*args, **kwargs) # noqa

# pylama:ignore=E1103,W0612
