import pytest

import muffin


@pytest.fixture(params=[
    pytest.param(('asyncio', {'use_uvloop': False}), id='asyncio'),
    pytest.param(('asyncio', {'use_uvloop': True}), id='asyncio+uvloop'),
    'trio', 'curio'
])
def aiolib(request):
    return request.param


@pytest.fixture
def app():
    """Simple basic app for testing."""
    app = muffin.Application('muffin', DEBUG=True)

    @app.route('/')
    async def index(request):
        return 'OK'

    return app


@pytest.fixture
def client(app, aiolib):
    return muffin.TestClient(app)
