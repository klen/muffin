import pytest
import muffin

from muffin.plugins import BasePlugin, PluginException


def test_plugins():
    with pytest.raises(TypeError):
        BasePlugin()

    class Plugin(BasePlugin):
        name = 'plugin'
        defaults = {
            'debug': True
        }

    pl1 = Plugin(test=42)

    assert pl1.cfg.test == 42

    app = muffin.Application(__name__, PLUGIN_DEBUG=False)
    app.install(pl1)
    assert pl1.name in app.ps
    assert not pl1.cfg.debug
    assert not pl1.frozen
    app.freeze()
    assert pl1.frozen
