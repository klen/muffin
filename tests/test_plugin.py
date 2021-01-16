from unittest import mock

import pytest
from asgi_lifespan import LifespanManager
from asgi_tools.tests import TestClient as Client


async def test_plugin(app, client):
    from muffin import BasePlugin, Application

    with pytest.raises(TypeError):
        BasePlugin()

    start = mock.MagicMock()
    finish = mock.MagicMock()

    class Plugin(BasePlugin):

        name = 'plugin'
        defaults = {
            'debug': True,
            'option': 42,
        }

        async def middleware(self, handler, request, receive, send):
            response = await handler(request, receive, send)
            response.headers['x-plugin'] = '42'
            return response

        async def startup(self):
            return start()

        def shutdown(self):
            return finish()

    plugin = Plugin(DEBUG=False)
    assert plugin.cfg
    assert plugin.cfg.debug is False

    app = Application('muffin', DEBUG=True, PLUGIN_DEBUG=True)
    plugin.init(app, option=43)

    assert plugin.cfg.debug is True
    assert plugin.cfg.option == 43

    assert app.lifespan._startup

    @app.route('/')
    async def index(request):
        return 'OK'

    assert not start.called
    assert not finish.called

    async with LifespanManager(app):

        assert start.called
        assert not finish.called

        client = Client(app)

        res = await client.get('/')
        assert res.status_code == 200
        assert res.text == 'OK'
        assert res.headers['x-plugin'] == '42'

    assert finish.called
