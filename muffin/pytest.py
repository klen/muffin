"""Support testing with Pytest."""

from __future__ import annotations

import logging
import os
from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING

import pytest
from asgi_tools.tests import ASGITestClient, manage_lifespan

from muffin.constants import CONFIG_ENV_VARIABLE
from muffin.utils import import_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from muffin.app import Application


def pytest_addoption(parser: pytest.Parser) -> None:
    """Append pytest options for testing Muffin apps."""
    parser.addini("muffin_app", "Set path to muffin application")
    parser.addoption(
        "--muffin-app",
        dest="muffin_app",
        help="Set to muffin application",
    )

    parser.addini("muffin_config", "Set module path to muffin configuration")
    parser.addoption(
        "--muffin-config",
        dest="muffin_config",
        help="Set module path to muffin configuration",
    )


def pytest_load_initial_conftests(
    early_config: pytest.Config, parser: pytest.Parser, args: list[str]
) -> None:
    """Prepare to loading Muffin application."""

    options = parser.parse_known_args(args)

    # Initialize configuration
    config = options.muffin_config or early_config.getini("muffin_config")
    if config:
        os.environ[CONFIG_ENV_VARIABLE] = config

    # Initialize application
    app_ = options.muffin_app or early_config.getini("muffin_app")
    setattr(early_config, "app", app_)  # noqa: B010


@pytest.fixture(scope="session")
async def app(
    pytestconfig: pytest.Config,
    request: pytest.FixtureRequest,  # noqa: ARG001
    aiolib: str,  # noqa: ARG001
) -> AsyncGenerator[Application, None]:
    """Load an application, run lifespan events, prepare plugins."""
    app_path = getattr(pytestconfig, "app", None)
    if not app_path:
        logging.warning(  # noqa: LOG015
            "Improperly configured. Please set ``muffin_app`` in your pytest config. "
            "Or use ``--muffin-app`` command option.",
        )
        return

    muffin_app = import_app(app_path)
    msg = f"Setup application '{muffin_app.cfg.name}'"
    if muffin_app.cfg.config:
        msg += f"with config '{muffin_app.cfg.config}'"
    muffin_app.logger.info(msg)

    # Setup plugins
    async with lifecycle(muffin_app):
        yield muffin_app


@asynccontextmanager
async def lifecycle(app: Application) -> AsyncGenerator[Application, None]:
    """Setup plugins and run lifespan events."""

    plugins = list(app.plugins.values())

    # Manage lifespan and prepare plugins
    async with AsyncExitStack() as stack:
        for plugin in plugins:
            await stack.enter_async_context(plugin.conftest())

        async with manage_lifespan(app):
            yield app


@pytest.fixture
def client(app: Application) -> ASGITestClient:
    """Generate a test client for the app."""
    return ASGITestClient(app)
