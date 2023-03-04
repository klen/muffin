"""Base Tests."""
from __future__ import annotations

from pathlib import Path
from unittest import mock


def test_imports():
    import muffin

    assert hasattr(muffin, "Request")
    assert hasattr(muffin, "Response")
    assert hasattr(muffin, "ResponseError")
    assert hasattr(muffin, "ResponseFile")
    assert hasattr(muffin, "ResponseHTML")
    assert hasattr(muffin, "ResponseJSON")
    assert hasattr(muffin, "ResponseRedirect")
    assert hasattr(muffin, "ResponseStream")
    assert hasattr(muffin, "ResponseText")
    assert hasattr(muffin, "ASGINotFoundError")
    assert hasattr(muffin, "ASGIInvalidMethodError")
    assert hasattr(muffin, "TestClient")


def test_app(app):
    assert app
    assert app.cfg.name == "muffin"
    assert repr(app) == "<muffin.Application: muffin>"


def test_app_config():
    import os

    import muffin

    os.environ["TEST_DEBUG"] = "true"

    app = muffin.Application(
        "tests.appcfg", config="unknown", name="test", LOG_CONFIG={"version": 1},
    )
    assert app.cfg
    assert app.cfg.CONFIG == "tests.appcfg"
    assert app.cfg.CONFIG_VARIABLE == 42
    assert app.cfg.DEBUG is True
    assert app.cfg.MANAGE_SHELL
    assert app.cfg.STATIC_URL_PREFIX == "/static"


async def test_routing(app, client):
    import re

    @app.route("/simple", re.compile("/simple/(a|b|c)/?$"), methods=["GET"])
    async def test(request):
        return 200, "simple"

    @app.route(r"/parameters/{param1}/{param2}")
    async def test_params(request):
        return 200, request.path_params

    res = await client.get("/simple")
    assert res.status_code == 200
    assert await res.text() == "simple"

    res = await client.post("/404")
    assert res.status_code == 404

    res = await client.post("/simple")
    assert res.status_code == 405

    res = await client.get("/simple/a")
    assert res.status_code == 200
    assert await res.text() == "simple"

    res = await client.get("/simple/b/")
    assert res.status_code == 200
    assert await res.text() == "simple"

    res = await client.get("/parameters/42/33")
    assert res.status_code == 200
    assert await res.json() == {"param1": "42", "param2": "33"}

    @app.route("/trim/last/slash/")
    async def test_last_slash(request):
        return "OK"

    res = await client.get("/trim/last/slash/")
    assert res.status_code == 200
    assert await res.text() == "OK"

    @app.route("/sync")
    def sync(request):
        return "Sync OK"

    res = await client.get("/sync")
    assert res.status_code == 200
    assert await res.text() == "Sync OK"


async def test_responses(app, client):
    @app.route("/none")
    async def test_none(request):
        return None

    @app.route("/bool")
    async def test_bool(request):
        return False

    @app.route("/str")
    async def test_str(request):
        return "str"

    @app.route("/bytes")
    async def test_bytes(request):
        return b"bytes"

    @app.route("/json")
    async def test_json(request):
        return {"test": "passed"}

    res = await client.get("/none")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    assert await res.json() is None

    res = await client.get("/bool")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    assert await res.json() is False

    res = await client.get("/str")
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/html; charset=utf-8"
    assert await res.text() == "str"

    res = await client.get("/bytes")
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/html; charset=utf-8"
    assert await res.text() == "bytes"

    res = await client.get("/json")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    assert await res.json() == {"test": "passed"}


async def test_websockets(app, client):
    from muffin import ResponseWebSocket

    @app.route("/stream")
    async def stream(request):
        ws = ResponseWebSocket(request)
        await ws.accept()
        msg = await ws.receive()
        assert msg == "ping"
        await ws.send("pong")
        await ws.close()

    async with client.websocket("/stream") as ws:
        await ws.send("ping")
        msg = await ws.receive()
        assert msg == "pong"


async def test_lifespan(app):
    import muffin

    start, finish = mock.MagicMock(), mock.MagicMock()

    app.on_startup(start)
    app.on_shutdown(finish)

    client = muffin.TestClient(app)
    async with client.lifespan():
        assert start.called
        assert not finish.called

        res = await client.get("/")
        assert res.status_code == 200

    assert start.called
    assert finish.called


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


async def test_error_handlers(client, app):
    import muffin

    @app.route("/500")
    async def raise_500(request):
        raise muffin.ResponseError(500)

    @app.route("/unhandled")
    async def raise_unhandled(request):
        raise Exception()  # noqa: TRY002

    @app.on_error(muffin.ResponseError)
    async def handler(request, response_error):
        if response_error.status_code == 404:
            return "Custom 404"
        return "Custom Server Error"

    @app.on_error(Exception)
    async def handle_exception(request, exc):
        return "Custom Unhandled"

    assert app.exception_handlers

    res = await client.get("/unhandled")
    assert res.status_code == 200
    assert await res.text() == "Custom Unhandled"

    res = await client.get("/500")
    assert res.status_code == 200
    assert await res.text() == "Custom Server Error"

    res = await client.get("/404")
    assert res.status_code == 200
    assert await res.text() == "Custom 404"

    del app.exception_handlers[muffin.ResponseError]


async def test_nested(client, app):
    @app.middleware
    async def mid(app, req, receive, send):
        response = await app(req, receive, send)
        if req.type == "http":
            response.headers["x-app"] = "OK"
        return response

    from muffin import Application

    subapp = Application()

    @subapp.route("/route")
    def subroute(request):
        return "OK from subroute"

    @subapp.middleware
    async def submid(app, req, receive, send):
        response = await app(req, receive, send)
        response.headers["x-subapp"] = "OK"
        return response

    app.route("/sub")(subapp)

    res = await client.get("/sub/route")
    assert res.status_code == 200
    assert await res.text() == "OK from subroute"
    assert res.headers["x-app"] == "OK"
    assert res.headers["x-subapp"] == "OK"


async def test_middlewares(app, client):
    @app.middleware
    async def simple_middleware(app, request, receive, send):
        response = await app(request, receive, send)

        if request.path == "/md/simple":
            response.headers["x-simple"] = "passed"

        return response

    @app.middleware
    def classic_middleware(app):
        async def middleware(scope, receive, send):
            async def custom_send(msg):
                if (
                    scope["path"] == "/md/classic"
                    and msg["type"] == "http.response.start"
                ):
                    msg["headers"].append((b"x-classic", b"passed"))
                await send(msg)

            await app(scope, receive, custom_send)

        return middleware

    @app.route("/md/simple")
    async def simple(request):
        return (200,)

    @app.route("/md/classic")
    async def classic(request):
        return (200,)

    res = await client.get("/")
    assert res.status_code == 200
    assert not res.headers.get("x-simple")
    assert not res.headers.get("x-classic")

    res = await client.get("/md/simple")
    assert res.status_code == 200
    assert res.headers["x-simple"] == "passed"
    assert not res.headers.get("x-classic")

    res = await client.get("/md/classic")
    assert res.status_code == 200
    assert not res.headers.get("x-simple")
    assert res.headers["x-classic"] == "passed"

# ruff: noqa: ARG001
