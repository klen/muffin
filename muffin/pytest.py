import logging
import os
import asyncio

import pytest

from aiohttp.pytest_plugin import pytest_addoption as aiohttp_pytest_addoption
from aiohttp.pytest_plugin import *  # noqa


def pytest_addoption(parser):
    """ Append pytest options for testing Muffin apps. """
    parser.addini('muffin_app', 'Set path to muffin application')
    parser.addoption('--muffin-app', dest='muffin_app', help='Set to muffin application')

    parser.addini('muffin_config', 'Set module path to muffin configuration')
    parser.addoption('--muffin-config', dest='muffin_config',
                     help='Set module path to muffin configuration')

    aiohttp_pytest_addoption(parser)


def pytest_load_initial_conftests(early_config, parser, args):
    """ Prepare to loading Muffin application. """
    from muffin import CONFIGURATION_ENVIRON_VARIABLE

    options = parser.parse_known_args(args)

    # Initialize configuration
    config = options.muffin_config or early_config.getini('muffin_config')
    if config:
        os.environ[CONFIGURATION_ENVIRON_VARIABLE] = config

    # Initialize application
    app_ = options.muffin_app or early_config.getini('muffin_app')
    early_config.app = app_


@pytest.fixture(scope='session')
def app(pytestconfig, request):
    """ Provide an example application. """
    from muffin.utils import to_coroutine
    from gunicorn import util

    if pytestconfig.app:
        app = util.import_app(pytestconfig.app)

        loop = asyncio.get_event_loop()
        for plugin in app.ps.values():
            if not hasattr(plugin, 'conftest'):
                continue
            loop.run_until_complete(to_coroutine(plugin.conftest)())

        return app

    logging.warn(
        'Improperly configured. Please set ``muffin_app`` in your pytest config. '
        'Or use ``--muffin-app`` command option.')

    return None


@pytest.fixture
async def client(app, aiohttp_client, loop):
    """Dirty hack for aiohttp tests."""
    app._loop = loop
    for subapp in app._subapps:
        subapp._loop = loop
    return await aiohttp_client(app)


#  pylama:ignore=W0212,W0621
