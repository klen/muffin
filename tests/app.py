"""Simple basic app for testing."""

from muffin import Application


app = Application(debug=True, name='muffin')


@app.route('/')
async def index(request):
    return 'OK'


@app.on_startup
async def start():
    app.state = 'started'
