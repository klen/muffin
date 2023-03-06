"""Base Tests."""
from __future__ import annotations

from pathlib import Path
from unittest import mock


def test_app_config():
    import os

    import muffin

    os.environ["TEST_DEBUG"] = "true"

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


def test_configure_logging():
    import muffin

    dummy = {"dummy": "dict", "version": 1}
    with mock.patch("muffin.app.dictConfig") as mocked:
        app = muffin.Application("muffin", LOG_CONFIG=dummy)
        assert app.logger
        assert app.logger.handlers
    mocked.assert_called_once_with(dummy)


async def test_static_folders():
    import muffin

    app = muffin.Application(
        static_folders=["tests", Path(__file__).parent.parent],
        static_url_prefix="/assets",
    )
    assert app.cfg.STATIC_FOLDERS
    assert app.cfg.STATIC_URL_PREFIX == "/assets"

    @app.route("/")
    async def index(request):
        return "OK"

    client = muffin.TestClient(app)
    res = await client.get("/")
    assert res.status_code == 200

    res = await client.get("/assets/test_application.py")
    assert res.status_code == 200
    text = await res.text()
    assert text.startswith('"""Base Tests."""')

    res = await client.get("/assets/pyproject.toml")
    assert res.status_code == 200


# ruff: noqa: ARG001
