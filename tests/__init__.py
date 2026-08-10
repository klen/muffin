"""Module-level app fixture for the pytest plugin (muffin_app = "tests:app").

Also used directly by tests/test_pytest.py.
"""

from muffin import Application

app = Application(debug=True, name="muffin")


@app.route("/")
async def index(request):
    return "OK"


@app.on_startup
async def start():
    app.state = "started"  # type: ignore[]
