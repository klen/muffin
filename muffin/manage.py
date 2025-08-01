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
from typing import TYPE_CHECKING, AsyncContextManager, Callable, overload

from muffin.constants import CONFIG_ENV_VARIABLE
from muffin.errors import AsyncRequiredError
from muffin.utils import AIOLIB, AIOLIBS, aio_lib, aio_run, import_app

if TYPE_CHECKING:
    from asgi_tools.types import TVCallable

    from .app import Application
    from .types import TVShellCtx

VERSION = metadata.version("muffin")
PARAM_RE = re.compile(r"^\s+:param (\w+): (.+)$", re.MULTILINE)


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
        self.parser = argparse.ArgumentParser(description="Manage %s" % app.cfg.name.capitalize())

        if len(AIOLIBS) > 1:
            self.parser.add_argument(
                "--aiolib",
                type=str,
                choices=list(AIOLIBS.keys()),
                default=aio_lib(),
                help="Select an asyncio library to run commands.",
            )

        self.subparsers = self.parser.add_subparsers(dest="subparser")
        self.commands: dict[str, Callable] = {}

        self.shell(
            getattr(
                app.cfg,
                "MANAGE_SHELL",
                lambda: dict(
                    app=app,
                    run=aio_run,
                    lifespan=app.lifespan,
                    **app.plugins,
                ),
            ),
        )

        # We have to use sync mode here because of eventloop conflict with ipython/promt-toolkit
        def shell(*, ipython: bool = True):
            """Start an interactive shell with the application context.

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

                    sh = InteractiveShellEmbed.instance(banner1=banner, user_ns=ctx)
                    return sh()

            code.interact(banner, local=ctx)

        self(shell)

        def run(host: str = "localhost", port: int = 5000):
            """Run the application with the given host and port."""
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
    def __call__(self, fn: "TVCallable") -> "TVCallable": ...

    @overload
    def __call__(self, *, lifespan: bool = False) -> Callable[["TVCallable"], "TVCallable"]: ...

    def __call__(self, fn=None, *, lifespan=False):  # noqa: C901
        """Register a command."""

        def wrapper(fn):  # noqa: C901, PLR0912
            if not inspect.iscoroutinefunction(fn) and lifespan:
                raise AsyncRequiredError(fn)

            fn.lifespan = lifespan

            description = "\n".join(
                [s for s in (fn.__doc__ or "").split("\n") if not s.strip().startswith(":")],
            ).strip()
            command_name = fn.__name__.replace("_", "-")
            if command_name in self.commands:
                self.app.logger.warning("Command %s already registered", command_name)
                return fn

            parser = self.subparsers.add_parser(
                command_name, description=description, help=description
            )
            sig = inspect.signature(fn)
            docs = dict(PARAM_RE.findall(fn.__doc__ or ""))

            for name, param in sig.parameters.items():
                arghelp = docs.get(name, "")
                argname = name.replace("_", "-")

                type_func = (
                    param.annotation
                    if param.annotation is not param.empty
                    else type(param.default) if param.default is not param.empty else str
                )
                if not isinstance(type_func, type):
                    type_func = str

                if param.kind == param.VAR_POSITIONAL:
                    parser.add_argument(name, nargs="*", metavar=name, help=arghelp)
                    continue

                if param.kind == param.VAR_KEYWORD:
                    # **kwargs not supported in CLI parser
                    continue

                if param.default is param.empty:
                    parser.add_argument(
                        name,
                        help=arghelp,
                        type=type_func,
                    )
                else:
                    default = param.default
                    if isinstance(default, bool):
                        if default:
                            parser.add_argument(
                                f"--no-{argname}",
                                dest=name,
                                action="store_false",
                                help=arghelp or f"Disable {name}",
                            )
                        else:
                            parser.add_argument(
                                f"--{argname}",
                                dest=name,
                                action="store_true",
                                help=arghelp or f"Enable {name}",
                            )
                    elif isinstance(default, list):
                        parser.add_argument(
                            f"--{argname}",
                            action="append",
                            default=default,
                            help=arghelp,
                        )
                    else:
                        parser.add_argument(
                            f"--{argname}",
                            type=(
                                param.annotation
                                if param.annotation is not param.empty
                                else type(default)
                            ),
                            default=default,
                            help=f"{arghelp} [{default!r}]",
                        )

            self.commands[command_name] = fn
            fn.parser = parser
            return fn

        if fn:
            return wrapper(fn)

        return wrapper

    def run(self, *args: str, prog: str | None = None):
        """Parse the arguments and run a command."""
        if prog:
            self.parser.prog = prog

        # Sort subparsers by name
        choices_actions = getattr(self.subparsers, "_choices_actions", None)
        if choices_actions:
            sorted_actions = sorted(choices_actions, key=lambda a: a.dest)
            choices_actions.clear()
            choices_actions.extend(sorted_actions)
            self.subparsers.metavar = "{" + ",".join(a.dest for a in sorted_actions) + "}"

        ns, _ = self.parser.parse_known_args(args or sys.argv[1:])
        kwargs = dict(ns._get_kwargs())
        fn = self.commands.get(kwargs.pop("subparser"))
        if "aiolib" in kwargs:
            AIOLIB.current = kwargs.pop("aiolib")

        if not fn:
            self.parser.print_help()
            sys.exit(1)

        pargs = []
        sig = inspect.signature(fn)
        for name, param in sig.parameters.items():
            if param.kind == param.VAR_POSITIONAL:
                pargs.extend(kwargs.pop(name, []))

        if not inspect.iscoroutinefunction(fn):
            return fn(*pargs, **kwargs)

        ctx: AsyncContextManager = AsyncExitStack()
        if getattr(fn, "lifespan", False):
            ctx = self.app.lifespan

        aio_run(run_fn, ctx, fn, args=pargs, kwargs=kwargs)


async def run_fn(ctx, fn, args=(), kwargs={}):  # noqa: B006
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

    except ImportError as exc:
        logging.error("Failed to import application: %s", exc)
        return sys.exit(1)

    try:
        app.manage.run(*subargs_, prog="muffin %s" % args_.app)
    except Exception:
        logging.exception("Command failed")
        return sys.exit(1)

    sys.exit(0)


# ruff: noqa: T100, LOG015, TRY400
