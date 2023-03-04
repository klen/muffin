"""CLI Support is here."""
import argparse
import code
import inspect
import logging
import os
import re
import sys
from contextlib import AsyncExitStack, suppress
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, AsyncContextManager, Callable, Mapping, Optional, overload

from muffin.constants import CONFIG_ENV_VARIABLE
from muffin.errors import AsyncRequiredError
from muffin.utils import AIOLIB, AIOLIBS, aio_lib, aio_run, import_app

if TYPE_CHECKING:
    from asgi_tools.types import TVCallable

    from .app import Application
    from .types import TVShellCtx

VERSION = metadata.version("muffin")
PARAM_RE = re.compile(r"^\s+:param (\w+): (.+)$", re.M)


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

    def __init__(self, app: "Application"):
        """Initialize the manager."""
        self.app = app
        self.parser = argparse.ArgumentParser(
            description="Manage %s" % app.cfg.name.capitalize(),
        )

        if len(AIOLIBS) > 1:
            self.parser.add_argument(
                "--aiolib",
                type=str,
                choices=list(AIOLIBS.keys()),
                default=aio_lib(),
                help="Select an asyncio library to run commands.",
            )

        self.subparsers = self.parser.add_subparsers(dest="subparser")
        self.commands: Mapping[str, Callable] = {}

        self.shell(
            getattr(
                app.cfg,
                "MANAGE_SHELL",
                lambda: dict(
                    app=app, run=aio_run, lifespan=app.lifespan, **app.plugins,
                ),
            ),
        )

        # We have to use sync mode here because of eventloop conflict with ipython/promt-toolkit
        def shell(*, ipython: bool = True):
            """Start the application's shell.

            :param ipython: Use IPython as a shell
            """
            banner = f"Interactive Muffin {VERSION} Shell"
            banner = f"\n{banner}\n{'-' * len(banner)}\nPython: {sys.version}\n\n"
            ctx = app.cfg.MANAGE_SHELL
            if callable(ctx):
                ctx = ctx()
            banner += f"Loaded globals: {list(ctx.keys())}\n"
            if ipython:
                with suppress(ImportError):
                    from IPython.terminal.embed import InteractiveShellEmbed

                    sh = InteractiveShellEmbed(banner1=banner, user_ns=ctx)
                    return sh()

            code.interact(banner, local=ctx)

        self(shell)

        def run(host: str = "localhost", port: int = 5000):
            """Start the application's server."""
            from uvicorn.main import run as urun

            cfg = self.app.cfg
            return urun(
                self.app,
                host=host,
                port=port,
                log_config=cfg.LOG_CONFIG,
            )

        self(run)

    def shell(self, ctx: "TVShellCtx") -> "TVShellCtx":
        """Set shell context. The method could be used as a decorator."""
        self.app.cfg.update(MANAGE_SHELL=ctx)
        return ctx

    def command(self, *args, **kwargs):
        """Just an alias for legacy code."""
        return self(*args, **kwargs)

    @overload
    def __call__(self, fn: "TVCallable") -> "TVCallable":
        ...

    @overload
    def __call__(self, *, lifespan: bool = False) -> Callable[["TVCallable"], "TVCallable"]:
        ...

    def __call__(self, fn=None, *, lifespan=False):  # noqa: C901
        """Register a command."""

        def wrapper(fn):  # noqa: C901
            if not inspect.iscoroutinefunction(fn) and lifespan:
                raise AsyncRequiredError(fn)

            fn.lifespan = lifespan

            description = "\n".join(
                [
                    s
                    for s in (fn.__doc__ or "").split("\n")
                    if not s.strip().startswith(":")
                ],
            ).strip()
            command_name = fn.__name__.replace("_", "-")
            if command_name in self.commands:
                self.app.logger.warning("Command %s already registered", command_name)
                return fn

            parser = self.subparsers.add_parser(command_name, description=description)
            args, vargs, _, defs, __, kwdefs, anns = inspect.getfullargspec(fn)
            defs = defs or []
            kwargs_ = dict(zip(args[-len(defs) :], defs))
            docs = dict(PARAM_RE.findall(fn.__doc__ or ""))

            def process_arg(name, *, value=..., **opts):
                argname = name.lower()
                arghelp = docs.get(name, "")
                if value is ...:
                    return parser.add_argument(argname, help=arghelp, **opts)

                argname = argname.replace("_", "-")
                if isinstance(value, bool):
                    if value:
                        return parser.add_argument(
                            "--no-" + argname,
                            dest=name,
                            action="store_false",
                            help=arghelp or f"Disable { name }",
                        )

                    return parser.add_argument(
                        "--" + argname,
                        dest=name,
                        action="store_true",
                        help=arghelp or f"Enable { name }",
                    )

                if isinstance(value, list):
                    return parser.add_argument(
                        "--" + argname, action="append", default=value, help=arghelp,
                    )

                return parser.add_argument(
                    "--" + argname,
                    type=anns.get(name, type(value)),
                    default=value,
                    help=arghelp + " [%s]" % repr(value),
                )

            if vargs:
                process_arg("*", nargs="*", metavar=vargs)

            for name, value in (kwdefs or {}).items():
                process_arg(name, value=value)

            for name in args:
                process_arg(name, value=kwargs_.get(name, ...))

            self.commands[command_name] = fn
            fn.parser = parser
            return fn

        if fn:
            return wrapper(fn)

        return wrapper

    def run(self, *args: str, prog: Optional[str] = None):
        """Parse the arguments and run a command."""
        if prog:
            self.parser.prog = prog

        ns, _ = self.parser.parse_known_args(args or sys.argv[1:])
        kwargs = dict(ns._get_kwargs())
        fn = self.commands.get(kwargs.pop("subparser"))
        if "aiolib" in kwargs:
            AIOLIB.current = kwargs.pop("aiolib")

        if not fn:
            self.parser.print_help()
            sys.exit(1)

        pargs = kwargs.pop("*", [])

        if not inspect.iscoroutinefunction(fn):
            return fn(*pargs, **kwargs)

        ctx: AsyncContextManager = AsyncExitStack()
        if getattr(fn, "lifespan", False):
            ctx = self.app.lifespan

        aio_run(run_fn, ctx, fn, args=pargs, kwargs=kwargs)


async def run_fn(ctx, fn, args=(), kwargs={}):  # noqa:
    """Run the given function with the given async context."""
    async with ctx:
        res = fn(*args, **kwargs)
        if inspect.isawaitable(res):
            await res


def cli():
    """Define main CLI endpoint."""
    sys.path.insert(0, Path.cwd().as_posix())
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

    parser = argparse.ArgumentParser(description="Manage Application", add_help=False)
    parser.add_argument("app", metavar="app", type=str, help="Application module path")
    parser.add_argument("--config", type=str, help="Path to configuration.")
    parser.add_argument("--version", action="version", version=VERSION)
    args_, subargs_ = parser.parse_known_args(sys.argv[1:])
    if args_.config:
        os.environ[CONFIG_ENV_VARIABLE] = args_.config

    try:
        app = import_app(args_.app)
        app.logger.info("Application is loaded: %s", app.cfg.name)
        app.manage.run(*subargs_, prog="muffin %s" % args_.app)

    except Exception:
        logging.exception()
        return sys.exit(1)

    sys.exit(0)

# ruff: noqa: T100
