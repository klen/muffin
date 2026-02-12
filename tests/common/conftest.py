import pytest

import muffin


@pytest.fixture
def app():
    """Simple basic app for testing."""

    app = muffin.Application(debug=True)

    @app.route("/")
    async def index(request):
        return "OK"

    return app
