import logging
import os

import pytest
from gunicorn import util

import muffin

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
    options = parser.parse_known_args(args)

    # Initialize configuration
    config = options.muffin_config or early_config.getini('muffin_config')
    if config:
        os.environ[muffin.CONFIGURATION_ENVIRON_VARIABLE] = config

    # Initialize application
    app_ = options.muffin_app or early_config.getini('muffin_app')
    early_config.app = app_


@pytest.fixture
def app(pytestconfig, request):
    """ Provide an example application. """
    if pytestconfig.app:
        return util.import_app(pytestconfig.app)

    logging.warn(
        'Improperly configured. Please set ``muffin_app`` in your pytest config. '
        'Or use ``--muffin-app`` command option.')
    return None


@pytest.fixture
def client(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))


@pytest.yield_fixture
def db(app):
    """ Run tests in transaction. """
    if 'peewee' not in app.plugins:
        yield None
    else:
        with app.ps.peewee.database.atomic() as trans:
            yield app.ps.peewee.database
            trans.rollback()


#  pylama:ignore=W0212,W0621
