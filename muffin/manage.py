"""CLI Support is here."""

import argparse
import inspect
import logging
import os
import re
import sys
import typing as t

from . import __version__, CONFIG_ENV_VARIABLE
from .app import Application
from .utils import aio_run, is_awaitable, import_app


PARAM_RE = re.compile(r'^\s+:param (\w+): (.+)$', re.M)
F = t.TypeVar('F', bound=t.Callable[..., t.Any])


class Manager:

    """Provide simple interface to make application's commands.

    ::

        @app.manage
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

    def __init__(self, app: Application):
        """Initialize the manager."""
        self.app = app
        self.parser = argparse.ArgumentParser(description="Manage %s" % app.name.capitalize())
        self.subparsers = self.parser.add_subparsers(dest='subparser')
        self.commands: t.Dict[str, t.Callable] = dict()

        app.cfg.update(MANAGE_SHELL=getattr(
            app.cfg, 'MANAGE_SHELL', lambda: dict(app=app, run=aio_run, **app.plugins)
        ))

        @self(lifespan=True)
        def shell(ipython: bool = True):
            """Run the application shell.

            :param ipython: Use IPython as a shell
            """
            banner = 'Interactive Muffin %s Shell' % __version__
            banner = '\n' + banner + '\n' + '-' * len(banner) + '\n\n'
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

    def __call__(self, lifespan: t.Union[bool, t.Callable] = False) -> t.Callable[[F], F]:
        """Register a command."""

        def wrapper(fn):
            description = '\n'.join([s for s in (fn.__doc__ or '').split('\n')
                                     if not s.strip().startswith(':')])
            parser = self.subparsers.add_parser(fn.__name__, description=description)
            args, vargs, kw, defs, kwargs, kwdefs, anns = inspect.getfullargspec(fn)
            defs = defs or []
            kwargs_ = dict(zip(args[-len(defs):], defs))
            docs = dict(PARAM_RE.findall(fn.__doc__ or ""))

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

            self.commands[fn.__name__] = fn
            fn.parser = parser
            return fn

        if callable(lifespan):
            lifespan.__lifespan = False  # type: ignore
            return wrapper(lifespan)

        def decorator(fn):
            fn.__lifespan = bool(lifespan)
            return wrapper(fn)

        return decorator

    def run(self, *args: str, prog: str = None):
        """Parse the arguments and run a command."""
        if prog:
            self.parser.prog = prog

        if not args:
            args = tuple(sys.argv[1:])

        ns, _ = self.parser.parse_known_args(args)
        kwargs = dict(ns._get_kwargs())

        command = self.commands.get(kwargs.pop('subparser'))
        if not command:
            self.parser.print_help()
            sys.exit(1)

        async def startup():
            for fn in self.app.lifespan._startup:
                await fn()

        async def shutdown():
            for fn in self.app.lifespan._shutdown:
                await fn()

        if command.__lifespan:  # type: ignore
            aio_run(startup)

        args = kwargs.pop('*', [])

        try:

            res = command(*args, **kwargs)
            if is_awaitable(res):
                aio_run(res)

            sys.exit(0)

        except Exception as exc:
            sys.exit(exc)

        finally:
            if command.__lifespan:  # type: ignore
                aio_run(shutdown)


def cli():
    """Define main CLI endpoint."""
    sys.path.insert(0, os.getcwd())
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

    parser = argparse.ArgumentParser(description="Manage Application", add_help=False)
    parser.add_argument('app', metavar='app',
                        type=str, help='Application module path')
    parser.add_argument('--config', type=str, help='Path to configuration.')
    parser.add_argument('--version', action="version", version=__version__)
    args_, subargs_ = parser.parse_known_args(sys.argv[1:])
    if args_.config:
        os.environ[CONFIG_ENV_VARIABLE] = args_.config

    try:
        app = import_app(args_.app)
        app.logger.info('Application is loaded: %s' % app.name)
    except Exception as exc:
        logging.exception(exc)
        raise sys.exit(1)

    app.manage.run(*subargs_, prog='muffin %s' % args_.app)
