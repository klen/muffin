import pytest
from asgi_tools._compat import aio_sleep


@pytest.fixture(params=["asyncio", "curio"], scope="session")
def aiolib(request):
    return request.param


@pytest.fixture()
def name(app):
    return app.cfg.name


async def test_app_imported(app):
    assert app.cfg.name == "muffin"


async def test_app_available_in_fixture(name):
    assert name == "muffin"


async def test_app_lifespan(app):
    assert app.state == "started"
