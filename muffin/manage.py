"""CLI Support is here."""

import argparse
import inspect
import logging
import os
import code
import re
import sys
import typing as t

from . import __version__, CONFIG_ENV_VARIABLE
from .app import Application
from .utils import aio_lib, aio_run, import_app, AIOLIBS, AIOLIB
from contextlib import AsyncExitStack


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
        self.parser = argparse.ArgumentParser(description="Manage %s" % app.cfg.name.capitalize())

        if len(AIOLIBS) > 1:
            self.parser.add_argument(
                '--aiolib', type=str, choices=list(AIOLIBS.keys()), default=aio_lib(),
                help='Select an asyncio library to run commands.')

        self.subparsers = self.parser.add_subparsers(dest='subparser')
        self.commands: t.Dict[str, t.Callable] = dict()

        self.shell(getattr(app.cfg, 'MANAGE_SHELL', lambda: dict(
            app=app, run=aio_run, lifespan=app.lifespan, **app.plugins)
        ))

        # We have to use sync mode here because of eventloop conflict with ipython/promt-toolkit
        @self
        def shell(ipython: bool = True):
            """Run the application shell.

            :param ipython: Use IPython as a shell
            """
            banner = f"Interactive Muffin {__version__} Shell"
            banner = f"\n{banner}\n{'-' * len(banner)}\nPython: {sys.version}\n\n"
            ctx = app.cfg.MANAGE_SHELL
            if callable(ctx):
                ctx = ctx()
            banner += f"Loaded globals: {list(ctx.keys())}\n"
            if ipython:
                try:
                    from IPython.terminal.embed import InteractiveShellEmbed
                    sh = InteractiveShellEmbed(banner1=banner, user_ns=ctx)
                    return sh()
                except ImportError:
                    pass

            code.interact(banner, local=ctx)

    def shell(self, ctx: t.Any) -> t.Any:
        """Set shell context. The method could be used as a decorator."""
        self.app.cfg.update(MANAGE_SHELL=ctx)
        return ctx

    def command(self, *args, **kwargs):
        """Just an alias for legacy code."""
        return self(*args, **kwargs)

    @t.overload
    def __call__(self, fn: F) -> F:
        ...

    @t.overload
    def __call__(self, *, lifespan: bool = False) -> t.Callable[[F], F]:
        ...

    def __call__(self, fn=None, lifespan=False):
        """Register a command."""

        def wrapper(fn):
            if not inspect.iscoroutinefunction(fn) and lifespan:
                raise ValueError('Muffin manage lifespan supported only for async functions.')

            fn.__lifespan = lifespan

            description = '\n'.join([s for s in (fn.__doc__ or '').split('\n')
                                     if not s.strip().startswith(':')]).strip()
            parser = self.subparsers.add_parser(fn.__name__, description=description)
            args, vargs, kw, defs, kwargs, kwdefs, anns = inspect.getfullargspec(fn)
            defs = defs or []
            kwargs_ = dict(zip(args[-len(defs):], defs))
            docs = dict(PARAM_RE.findall(fn.__doc__ or ''))

            def process_arg(name, *, value=..., **opts):
                argname = name.lower()
                arghelp = docs.get(name, '')
                if value is ...:
                    return parser.add_argument(argname, help=arghelp, **opts)

                argname = argname.replace('_', '-')
                if isinstance(value, bool):
                    if value:
                        return parser.add_argument(
                            "--no-" + argname, dest=name, action="store_false",
                            help=arghelp or f"Disable { name }")

                    return parser.add_argument(
                        "--" + argname, dest=name, action="store_true",
                        help=arghelp or f"Enable { name }")

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

        if fn:
            return wrapper(fn)

        return wrapper

    def run(self, *args: str, prog: str = None):
        """Parse the arguments and run a command."""
        if prog:
            self.parser.prog = prog

        if not args:
            args = tuple(sys.argv[1:])

        ns, _ = self.parser.parse_known_args(args)
        kwargs = dict(ns._get_kwargs())
        fn = self.commands.get(kwargs.pop('subparser'))
        if 'aiolib' in kwargs:
            AIOLIB.current = kwargs.pop('aiolib')

        if not fn:
            self.parser.print_help()
            sys.exit(1)

        args, kwargs = kwargs.pop('*', []), kwargs

        if not inspect.iscoroutinefunction(fn):
            return fn(*args, **kwargs)

        ctx: t.AsyncContextManager = AsyncExitStack()
        if fn.__lifespan:  # type: ignore
            ctx = self.app.lifespan

        aio_run(run_fn, ctx, fn, args=kwargs.pop('*', []), kwargs=kwargs)


async def run_fn(ctx, fn, args=(), kwargs={}):
    """Run the given function with the given async context."""
    async with ctx:
        res = fn(*args, **kwargs)
        if inspect.isawaitable(res):
            await res


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
        app.logger.info('Application is loaded: %s' % app.cfg.name)
        app.manage.run(*subargs_, prog='muffin %s' % args_.app)

    except Exception as exc:
        logging.exception(exc)
        raise sys.exit(1)

    sys.exit(0)


# pylama: ignore=W0404,D
