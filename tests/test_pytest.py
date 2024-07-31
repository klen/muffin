import pytest
from asgi_tools._compat import aio_sleep


@pytest.fixture()
def name(app):
    return app.cfg.name


async def test_app_imported(app):
    assert app.cfg.name == "muffin"
    await aio_sleep(0.2)


async def test_app_available_in_fixture(name):
    assert name == "muffin"
    await aio_sleep(0.2)


async def test_app_lifespan(app):
    assert app.state == "started"
    await aio_sleep(0.2)
