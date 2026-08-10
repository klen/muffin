import muffin


def test_app_config(monkeypatch):
    monkeypatch.setenv("TEST_DEBUG", "true")

    app = muffin.Application(
        "tests.config_fixture",
        config="unknown",
        name="test",
        LOG_CONFIG={"version": 1},
    )
    assert app.cfg
    assert app.cfg.CONFIG == "tests.config_fixture"
    assert app.cfg.CONFIG_VARIABLE == 42
    assert app.cfg.DEBUG is True
    assert app.cfg.MANAGE_SHELL
    assert app.cfg.STATIC_URL_PREFIX == "/static"
