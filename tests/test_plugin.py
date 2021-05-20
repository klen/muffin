from unittest import mock

import pytest


@pytest.fixture
def app():
    from muffin import Application

    return Application()


async def test_plugin_config(app, client):
    from muffin import Application
    from muffin.plugins import BasePlugin

    class Plugin(BasePlugin):

        name = 'plugin'
        defaults = {
            'debug': True,
            'option': 11,
        }

        after_setup = True

        def setup(self, app, **options):
            super(Plugin, self).setup(app, **options)
            self.after_setup = self.cfg.option

    plugin = Plugin(debug=False)
    assert plugin.cfg
    assert plugin.cfg.debug is False

    app = Application('tests.appcfg')

    plugin = Plugin(app)
    assert plugin.cfg.option == 42  # from application config

    plugin = Plugin(app, option=22)
    assert plugin.cfg.option == 22
    assert plugin.after_setup == 22


async def test_plugin(app, client):
    from muffin import Application, TestClient
    from muffin.plugins import BasePlugin

    with pytest.raises(TypeError):
        BasePlugin()

    start = mock.MagicMock()
    finish = mock.MagicMock()
    assert BasePlugin.middleware is None
    assert BasePlugin.startup is None
    assert BasePlugin.shutdown is None

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
    plugin.setup(app, option=43)
    assert plugin.app is app
    assert app.plugins['plugin'] is plugin

    assert plugin.cfg.debug is True
    assert plugin.cfg.option == 43

    @app.route('/')
    async def index(request):
        return 'OK'

    assert not start.called
    assert not finish.called

    client = TestClient(app)

    async with client.lifespan():

        assert start.called
        assert not finish.called

        res = await client.get('/')
        assert res.status_code == 200
        assert res.headers['x-plugin'] == '42'
        assert await res.text() == 'OK'

    assert finish.called


def test_multi_plugins(app):
    from muffin.plugins import BasePlugin

    class Plugin(BasePlugin):

        name = 'plugin'

    p1 = Plugin(app, name='plugin1')
    p2 = Plugin(app, name='plugin2')

    assert p1.name == 'plugin1'
    assert p2.name == 'plugin2'

    assert app.plugins == {
        'plugin1': p1,
        'plugin2': p2,
    }
