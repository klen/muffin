import pytest
import muffin
import asyncio

from muffin.plugins import BasePlugin, PluginException


def test_plugins():
    with pytest.raises(TypeError):
        BasePlugin()

    class Plugin(BasePlugin):
        name = 'plugin'
        defaults = {
            'debug': True
        }

        def middleware(self, request, handler):
            return handler(request)

        def startup(self, app):
            return 1

    pl1 = Plugin(test=42)
    assert asyncio.iscoroutinefunction(pl1.middleware)
    assert asyncio.iscoroutinefunction(pl1.startup)

    assert pl1.cfg.test == 42

    app = muffin.Application(__name__, PLUGIN_DEBUG=False)
    app.install(pl1)
    assert pl1.name in app.ps
    assert not pl1.cfg.debug
    assert not pl1.frozen
    app.freeze()
    assert pl1.frozen
