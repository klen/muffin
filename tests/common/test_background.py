from asgi_tools._compat import aio_sleep


async def test_background(app, client):
    results = []

    async def background_task(param):
        await aio_sleep(1e-1)
        results.append(param)

    @app.route("/background")
    async def background(request):
        app.run_background(background_task("test"))
        return "OK"

    res = await client.get("/background")
    assert res.status_code == 200
    assert results == ["test"]
