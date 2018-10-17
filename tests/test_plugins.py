import pytest
import muffin

from muffin.plugins import BasePlugin, PluginException


def test_plugins():
    with pytest.raises(PluginException):
        BasePlugin()

    class Plugin(BasePlugin):
        name = 'plugin'
        defaults = {
            'debug': True
        }

    pl1 = Plugin(test=42)
    pl2 = Plugin(test=24)

    assert pl1 is pl2
    assert pl1.cfg.test == 42

    app = muffin.Application(__name__, PLUGIN_DEBUG=False)
    app.install(pl1)
    assert pl1.name in app.ps
    assert not pl1.cfg.debug
