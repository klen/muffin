import pytest


async def test_handler(app, client):
    from muffin.handler import Handler, route_method

    @app.route("/handler", "/handler/{res}")
    class Index(Handler):
        async def get(self, request):
            return request.path_params or "ok"

        async def post(self, request):
            data = await request.data()
            return dict(data)

        @Handler.route("/custom1", methods=["put", "patch"])
        async def custom1(self, request):
            return self.__class__.__name__

        @route_method("/custom2")
        async def custom2(self, request):
            return "CUSTOM2"

    assert Index.methods
    assert sorted(Index.methods) == ["GET", "POST"]

    res = await client.get("/handler")
    assert res.status_code == 200
    assert await res.text() == "ok"

    res = await client.get("/handler/123")
    assert res.status_code == 200
    assert await res.json() == {"res": "123"}

    res = await client.post("/handler", json={"test": "passed"})
    assert res.status_code == 200
    assert await res.json() == {"test": "passed"}

    res = await client.put("/handler")
    assert res.status_code == 405
    assert await res.text() == "Specified method is invalid for this resource"

    res = await client.put("/custom1")
    assert res.status_code == 200
    assert await res.text() == "Index"

    res = await client.get("/custom1")
    assert res.status_code == 405

    res = await client.get("/custom2")
    assert res.status_code == 200
    assert await res.text() == "CUSTOM2"


async def test_deffered(app, client):
    from muffin.handler import Handler

    class Resource(Handler):
        methods = "post"

        async def get(self, request):
            raise RuntimeError

        async def post(self, request):
            return "Resource is here"

        @Handler.route("/resource/custom")
        async def custom(self, request):
            return "Resource Custom is here"

    assert Resource.methods == {"POST"}

    app.route("/resource")(Resource)

    res = await client.get("/resource")
    assert res.status_code == 405

    res = await client.post("/resource")
    assert res.status_code == 200
    assert await res.text() == "Resource is here"

    res = await client.post("/resource/custom")
    assert res.status_code == 200
    assert await res.text() == "Resource Custom is here"
