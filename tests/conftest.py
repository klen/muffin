# Configure your tests here

import pytest


@pytest.fixture(scope='session')
def app():
    """ Provide an example application. """
    from app import app

    return app
