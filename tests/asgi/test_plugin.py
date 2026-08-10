from typing import ClassVar
from unittest import mock

import pytest

from muffin import Application, TestClient
from muffin.plugins import BasePlugin


class ConfigPlugin(BasePlugin):
    name = "plugin"
    defaults: ClassVar = {"debug": True, "option": 11}

    after_setup = True

    def setup(self, app, **options):
        super(ConfigPlugin, self).setup(app, **options)
        self.after_setup = self.cfg.option


async def test_plugin_config_from_plugin_defaults():
    plugin = ConfigPlugin(debug=False)
    assert plugin.cfg
    assert plugin.cfg.debug is False
    assert plugin.cfg.disabled is False  # disabled injected automatically


async def test_plugin_config_from_application_config():
    app = Application("tests.config_fixture")
    plugin = ConfigPlugin(app)
    assert plugin.cfg.option == 42  # from application config


async def test_plugin_config_from_env(monkeypatch):
    app = Application()
    monkeypatch.setenv("MUFFIN_PLUGIN_OPTION", "33")
    plugin = ConfigPlugin(app)
    assert plugin.cfg.option == 33  # from env


async def test_plugin_config_from_options():
    app = Application("tests.config_fixture")
    plugin = ConfigPlugin(app, option=22)
    assert plugin.cfg.option == 22
    assert plugin.after_setup == 22


async def test_base_plugin_requires_name(app):
    with pytest.raises(TypeError):
        BasePlugin(app)


async def test_plugin_setup_registers_and_applies_config():
    start = mock.MagicMock()
    finish = mock.MagicMock()

    class Plugin(BasePlugin):
        name = "plugin"
        defaults: ClassVar = {"debug": True, "option": 42}

        async def middleware(self, handler, request, receive, send):
            response = await handler(request, receive, send)
            response.headers["x-plugin"] = "42"
            return response

        async def startup(self):
            return start()

        def shutdown(self):
            return finish()

    plugin = Plugin(DEBUG=False)
    assert plugin.cfg
    assert plugin.cfg.debug is False

    app = Application("muffin", DEBUG=True, PLUGIN_DEBUG=True)
    plugin.setup(app, option=43)
    assert plugin.app is app
    assert app.plugins["plugin"] is plugin

    assert plugin.cfg.debug is True
    assert plugin.cfg.option == 43

    assert not start.called
    assert not finish.called


async def test_plugin_middleware_adds_header():
    class Plugin(BasePlugin):
        name = "plugin"

        async def middleware(self, handler, request, receive, send):
            response = await handler(request, receive, send)
            response.headers["x-plugin"] = "42"
            return response

    app = Application("muffin")
    Plugin(app)

    @app.route("/")
    async def index(request):
        return "OK"

    client = TestClient(app)
    async with client.lifespan():
        res = await client.get("/")
        assert res.status_code == 200
        assert res.headers["x-plugin"] == "42"
        assert await res.text() == "OK"


async def test_plugin_lifespan_calls_startup_and_shutdown():
    start = mock.MagicMock()
    finish = mock.MagicMock()

    class Plugin(BasePlugin):
        name = "plugin"

        async def startup(self):
            return start()

        def shutdown(self):
            return finish()

    app = Application("muffin")
    Plugin(app)
    client = TestClient(app)

    assert not start.called
    assert not finish.called

    async with client.lifespan():
        assert start.called
        assert not finish.called

    assert finish.called


def test_multi_plugins(app):
    class Plugin(BasePlugin):
        name = "plugin"

    p1 = Plugin(app, name="plugin1")
    p2 = Plugin(app, name="plugin2")

    assert p1.name == "plugin1"
    assert p2.name == "plugin2"

    assert app.plugins == {
        "plugin1": p1,
        "plugin2": p2,
    }


async def test_plugin_as_context_manager():
    events = []

    class Plugin(BasePlugin):
        name = "plugin"

        async def startup(self):
            events.append("start")

        async def shutdown(self):
            events.append("end")

    plug = Plugin()
    async with plug:
        pass

    assert "start" in events
    assert "end" in events
