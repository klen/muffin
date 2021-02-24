import pytest

import muffin


@pytest.fixture(params=[
    pytest.param('asyncio'),
    pytest.param('trio'),
    pytest.param('curio'),
])
def anyio_backend(request):
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
def client(app, anyio_backend):
    return muffin.TestClient(app)
