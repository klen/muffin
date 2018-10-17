async def test_example(aiohttp_client):
    import muffin

    app = muffin.Application('example')

    @app.register('/', '/hello/{name}')
    def hello(request):
        name = request.match_info.get('name', 'anonymous')
        return 'Hello %s!' % name

    client = await aiohttp_client(app)

    async with client.get('/', raise_for_status=True) as resp:
        text = await resp.text()
        assert text == 'Hello anonymous!'

    async with client.get('/hello/tester', raise_for_status=True) as resp:
        text = await resp.text()
        assert text == 'Hello tester!'


async def test_async_code():
    async def coro():
        return True

    assert await coro()


def test_app(app):
    assert app.name == 'muffin'
    assert app.cfg.DEBUG is ...


async def test_view(client):
    """ Make HTTP request to your application. """
    async with client.get('/') as resp:
        text = await resp.text()
        assert text == 'OK'
