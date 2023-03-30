"""Implement Muffin Application."""
from __future__ import annotations

import logging
from contextvars import ContextVar
from inspect import isawaitable, stack
from logging.config import dictConfig
from typing import TYPE_CHECKING, Any, Dict, Final, Mapping, Union

from asgi_tools import App as BaseApp
from asgi_tools._compat import aio_wait
from modconfig import Config

from muffin.constants import CONFIG_ENV_VARIABLE
from muffin.utils import import_submodules

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from types import ModuleType

    from asgi_tools.types import TASGIReceive, TASGIScope, TASGISend

    from muffin.plugins import BasePlugin

BACKGROUND_TASK: Final["ContextVar[set[Awaitable] | None]"] = ContextVar(
    "background_tasks",
    default=None,
)


class Application(BaseApp):
    """The Muffin Application."""

    # Default configuration values
    defaults: Mapping[str, Any] = {
        # The application's name
        "NAME": "muffin",
        # Path to configuration module
        "CONFIG": None,
        # Enable debug mode (optional)
        "DEBUG": False,
        # Routing options
        "TRIM_LAST_SLASH": True,
        # Static files options
        "STATIC_URL_PREFIX": "/static",
        "STATIC_FOLDERS": [],
        # Logging options
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
        "LOG_DATE_FORMAT": "[%Y-%m-%d %H:%M:%S]",
        "LOG_CONFIG": None,
    }

    def __init__(self, *cfg_mods: Union[str, ModuleType], **options):
        """Initialize the application.

        :param *cfg_mods: modules to import application's config
        :param **options: Configuration options

        """
        self.plugins: Dict[str, BasePlugin] = {}

        # Setup the configuration
        self.cfg = Config(**self.defaults, config_config={"update_from_env": False})
        options["CONFIG"] = self.cfg.update_from_modules(
            *cfg_mods,
            f"env:{CONFIG_ENV_VARIABLE}",
        )
        self.cfg.update(**options)
        self.cfg.update_from_env(prefix=f"{ self.cfg.name }_")

        # Setup CLI
        from muffin.manage import Manager

        self.manage = Manager(self)

        # Setup logging
        log_config = self.cfg.get("LOG_CONFIG")
        if log_config and isinstance(log_config, dict) and log_config.get("version"):
            dictConfig(log_config)

        self.logger = logging.getLogger("muffin")
        self.logger.setLevel(self.cfg.LOG_LEVEL)
        self.logger.propagate = False
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(
                logging.Formatter(self.cfg.LOG_FORMAT, self.cfg.LOG_DATE_FORMAT),
            )
            self.logger.addHandler(ch)

        super().__init__(
            debug=self.cfg.DEBUG,
            logger=self.logger,
            trim_last_slash=self.cfg.TRIM_LAST_SLASH,
            static_folders=self.cfg.STATIC_FOLDERS,
            static_url_prefix=self.cfg.STATIC_URL_PREFIX,
        )

    def __repr__(self) -> str:
        """Human readable representation."""
        return f"<muffin.Application: { self.cfg.name }>"

    async def __call__(
        self,
        scope: TASGIScope,
        receive: TASGIReceive,
        send: TASGISend,
    ):
        """Support background tasks."""
        await self.lifespan(scope, receive, send)
        bgtasks = BACKGROUND_TASK.get()
        if bgtasks is not None:
            await aio_wait(*bgtasks)
            BACKGROUND_TASK.set(None)

    def import_submodules(self, *submodules: str):
        """Automatically import submodules.

        .. code-block:: python

            # Somewhere in package "__init__.py" file

            # import all submodules
            app.import_submodules()

            # import only specific submodules (in specified order)
            app.import_submodules('submodule1', 'submodule2')

        """
        parent_frame = stack()[1][0]
        package_name = parent_frame.f_locals["__name__"]
        return import_submodules(package_name, *submodules)

    def run_after_response(self, *tasks: Awaitable):
        """Await the given awaitable after the response is completed.

        .. code-block:: python

            from muffin import Application

            app = Application()

            @app.task
            def send_email(email, message):
                # send email here
                pass

            @app.route('/send')
            async def send(request):

            # Schedule any awaitable for later execution
            app.run_after_response(send_email('user@email.com', 'Hello from Muffin!'))

            # Return response to a client immediately
            # The task will be executed after the response is sent
            return "OK"

        """
        scheduled = BACKGROUND_TASK.get() or set()
        for task in tasks:
            if not isawaitable(task):
                raise TypeError(f"Task must be awaitable: {task!r}")  # noqa: TRY003

            scheduled.add(task)

        BACKGROUND_TASK.set(scheduled)
