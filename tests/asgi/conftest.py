import pytest
from asgi_tools.tests import ASGITestClient

import muffin


@pytest.fixture
def app():
    """Function-scoped app for ASGI integration tests."""
    app = muffin.Application(debug=True)

    @app.route("/")
    async def index(request):
        return "OK"

    return app


@pytest.fixture
def client(app):
    """Test client bound to the function-scoped app."""
    return ASGITestClient(app)
