import pytest


@pytest.fixture()
def app():
    """Simple basic app for testing."""
    import muffin

    app = muffin.Application(debug=True)

    @app.route("/")
    async def index(request):
        return "OK"

    return app
