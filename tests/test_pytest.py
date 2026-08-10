import pytest
from asgi_tools._compat import aio_sleep


# Only asyncio and curio are compatible with the pytest plugin;
# trio and uvloop are skipped here (they are covered in common/ tests).
@pytest.fixture(params=["asyncio", "curio"], scope="session")
def aiolib(request):
    return request.param


@pytest.fixture
def name(app):
    return app.cfg.name


async def test_app_imported(app):
    assert app.cfg.name == "muffin"


async def test_app_available_in_fixture(name):
    assert name == "muffin"


async def test_app_lifespan(app):
    assert app.state == "started"
