import re
from unittest import mock

from asgi_tools._compat import aio_sleep

import muffin
from muffin import Application, ResponseWebSocket


async def test_routing(app, client):

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
                if scope["path"] == "/md/classic" and msg["type"] == "http.response.start":
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


async def test_nested(client, app):
    @app.middleware
    async def mid(app, req, receive, send):
        response = await app(req, receive, send)
        if req.type == "http":
            response.headers["x-app"] = "OK"
        return response

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


async def test_error_handlers(client, app):
    @app.route("/500")
    async def raise_500(request):
        raise muffin.ResponseError(500)

    @app.route("/unhandled")
    async def raise_unhandled(request):
        raise Exception()

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


async def test_run_after(app, client):
    results = []

    async def background_task(param):
        await aio_sleep(1e-1)
        results.append(param)

    @app.route("/background")
    async def background(request):
        app.run_after_response(background_task("bg1"))
        app.run_after_response(
            background_task("bg2"),
            background_task("bg3"),
        )
        return "OK"

    res = await client.get("/background")
    assert res.status_code == 200
    assert set(results) == {"bg1", "bg2", "bg3"}
