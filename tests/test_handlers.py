import muffin
import asyncio


async def test_handler(aiohttp_client):
    """Test class-based handlers.

    Actually everything in Muffin is class-based handlers.
    Because view-functions will convert to Handler classes.
    """
    from muffin.handler import register

    app = muffin.Application('test')

    @app.register('/res(/{res})?/?')
    @app.register('/res/{res}')
    class Resource(muffin.Handler):

        def get(self, request):
            return request.match_info

        async def post(self, request):
            data = await self.parse(request)
            return dict(data)

        @register('/res/lama/rama', methods=['GET', 'POST', 'PATCH'])
        def lama(self, request):
            return 'LAMA'

        @register('/res/rama/lama')
        def rama(self, request):
            return 'RAMA'

    assert set(Resource.methods) == set(['GET', 'POST'])
    assert asyncio.iscoroutinefunction(Resource.get)

    @app.register('/res2(/{res2})?/?')
    class Resource2(muffin.Handler):

        methods = 'get',

        def get(self, request):
            return 'OK'

        def put(self, request):
            raise Exception('Must not be called')

    @Resource2.register('/connect')
    def connect_(handler, request):
        return handler.app.name

    assert 'resource' in app.router
    assert 'resource.lama' in app.router
    assert 'resource.rama' in app.router

    client = await aiohttp_client(app)

    async with client.get('/res/lama/rama') as resp:
        text = await resp.text()
        assert text == 'LAMA'

    async with client.patch('/res/lama/rama') as resp:
        text = await resp.text()
        assert text == 'LAMA'

    async with client.get('/res/rama/lama') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'RAMA'

    async with client.delete('/res') as resp:
        assert resp.status == 405

    async with client.get('/res') as resp:
        assert resp.status == 200
        json = await resp.json()
        assert json == {'res': ''}

    async with client.get('/res/passed') as resp:
        assert resp.status == 200
        json = await resp.json()
        assert json == {'res': 'passed'}

    async with client.post('/res', data={'form': 'value'}) as resp:
        assert resp.status == 200
        json = await resp.json()
        assert json == {'form': 'value'}

    async with client.post('/res', json={'json': 'value'}) as resp:
        assert resp.status == 200
        json = await resp.json()
        assert json == {'json': 'value'}

    async with client.get('/res2') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'OK'

    async with client.put('/res2') as resp:
        assert resp.status == 405

    async with client.get('/res2') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'OK'

    async with client.get('/connect') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test'


async def test_handler_func(aiohttp_client):
    """Test convert functions to Muffin's Handlers."""

    app = muffin.Application('test')

    @app.register('/test1')
    def test1(request):
        return 'test1 passed'

    assert 'test1' in app.router

    @app.register('/test2', methods='put')
    def test2(request):
        return 'test2 passed'

    @app.register('/test3', methods=('get', 'post'))
    def test3(request):
        return 'test3 passed'

    @app.register('/test4', methods='*')
    def test4(request):
        return 'test4 passed'

    def test5(request):
        return 'test5 passed'

    app.register('/test5')(muffin.Handler.from_view(test5))

    client = await aiohttp_client(app)

    async with client.get('/test1') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test1 passed'

    async with client.post('/test1') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test1 passed'

    async with client.put('/test2') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test2 passed'

    async with client.post('/test3') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test3 passed'

    async with client.get('/test4') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test4 passed'

    async with client.post('/test4') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test4 passed'

    async with client.delete('/test4') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test4 passed'

    async with client.get('/test5') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'test5 passed'


async def test_deffered(aiohttp_client):

    class Resource3(muffin.Handler):

        methods = 'get',

        def get(self, request):
            return 'Resource3'

    @Resource3.register('/dummy')
    def dummy(handler, request):
        return 'dummy here'

    app = muffin.Application('test')
    app.register('/resource-3')(Resource3)

    client = await aiohttp_client(app)
    async with client.get('/resource-3') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'Resource3'

    async with client.get('/dummy') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'dummy here'


async def test_responses(aiohttp_client):

    app = muffin.Application('test')

    @app.register('/none')
    def none(request):
        return None

    @app.register('/str')
    def str(request):
        return 'str'

    @app.register('/bytes')
    def bytes(request):
        return b'bytes'

    @app.register('/json')
    def json(request):
        return {'test': 'passed'}

    client = await aiohttp_client(app)

    async with client.get('/none') as resp:
        assert resp.status == 200
        assert resp.content_type == 'application/json'

        text = await resp.text()
        assert text == 'null'

    async with client.get('/json') as resp:
        assert resp.status == 200
        assert resp.content_type == 'application/json'

        json = await resp.json()
        assert json == {'test': 'passed'}

    async with client.get('/str') as resp:
        assert resp.status == 200
        assert resp.content_type == 'text/html'

        text = await resp.text()
        assert text == 'str'

    async with client.get('/bytes') as resp:
        assert resp.status == 200
        assert resp.content_type == 'text/html'

        text = await resp.text()
        assert text == 'bytes'


async def test_custom_methods(aiohttp_client):

    app = muffin.Application('test')

    @app.register('/caldav', methods='PROPFIND')
    def propfind(request):
        return b'PROPFIND'

    client = await aiohttp_client(app)

    resp = await client.request('PROPFIND', '/caldav')
    assert resp.status == 200

    text = await resp.text()
    assert text == 'PROPFIND'
    resp.close()
