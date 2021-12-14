"""Support testing with Pytest."""

import logging
import os

import pytest
from asgi_tools.tests import ASGITestClient, manage_lifespan


def pytest_addoption(parser):
    """Append pytest options for testing Muffin apps."""
    parser.addini("muffin_app", "Set path to muffin application")
    parser.addoption(
        "--muffin-app", dest="muffin_app", help="Set to muffin application"
    )

    parser.addini("muffin_config", "Set module path to muffin configuration")
    parser.addoption(
        "--muffin-config",
        dest="muffin_config",
        help="Set module path to muffin configuration",
    )


def pytest_load_initial_conftests(early_config, parser, args):
    """Prepare to loading Muffin application."""
    from muffin import CONFIG_ENV_VARIABLE

    options = parser.parse_known_args(args)

    # Initialize configuration
    config = options.muffin_config or early_config.getini("muffin_config")
    if config:
        os.environ[CONFIG_ENV_VARIABLE] = config

    # Initialize application
    app_ = options.muffin_app or early_config.getini("muffin_app")
    early_config.app = app_


@pytest.fixture(scope="session")
async def app(pytestconfig, request, aiolib):
    """Load an application, run lifespan events, prepare plugins."""
    if not pytestconfig.app:
        logging.warning(
            "Improperly configured. Please set ``muffin_app`` in your pytest config. "
            "Or use ``--muffin-app`` command option."
        )
        return

    from muffin.utils import import_app

    app_ = import_app(pytestconfig.app)
    msg = f"Setup application '{app_.cfg.name}'"
    if app_.cfg.config:
        msg += f"with config '{app_.cfg.config}'"
    app_.logger.info(msg)

    async with manage_lifespan(app_):

        # Setup plugins
        for plugin in app_.plugins.values():
            if hasattr(plugin, "conftest") and plugin.conftest is not None:
                app_.logger.info(f"Setup plugin '{plugin.name}'")
                await plugin.conftest()

        yield app_


@pytest.fixture
def client(app):
    """Generate a test client for the app."""
    return ASGITestClient(app)
