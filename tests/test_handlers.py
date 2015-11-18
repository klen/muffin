import muffin
import asyncio


def test_handler(app, client):
    """Test class-based handlers.

    Actually everything in Muffin is class-based handlers.
    Because view-functions will convert to Handler classes.
    """
    from muffin.handler import register

    @app.register(muffin.sre('/res(/{res})?/?'))
    @app.register('/res/{res}')
    class Resource(muffin.Handler):

        def get(self, request):
            return request.match_info

        def post(self, request):
            data = yield from self.parse(request)
            return dict(data)

        @register('/res/lama/rama', methods=['GET', 'POST', 'PATCH'])
        def lama(self, request):
            return 'LAMA'

        @register('/res/rama/lama')
        def rama(self, request):
            return 'RAMA'

    assert set(Resource.methods) == set(['GET', 'POST'])
    assert asyncio.iscoroutinefunction(Resource.get)

    assert 'resource.any' in app.router._routes

    response = client.get('/res/lama/rama')
    assert response.text == 'LAMA'
    assert 'lama.post' in app.router
    assert 'lama.patch' in app.router

    response = client.get('/res/rama/lama')
    assert response.text == 'RAMA'

    response = client.delete('/res', status=405)

    response = client.get('/res')
    assert response.json == {'res': ''}

    response = client.get('/res/1')
    assert response.json == {'res': '1'}

    response = client.get('/res/2/')
    assert response.json == {'res': '2'}

    response = client.post('/res', {'data': 'form'})
    assert response.json == {'data': 'form'}

    response = client.post_json('/res', {'data': 'json'})
    assert response.json == {'data': 'json'}

    @app.register(muffin.sre('/res2(/{res2})?/?'))
    class Resource2(muffin.Handler):

        methods = 'get',

        def get(self, request):
            return 'OK'

        def put(self, request):
            raise Exception('Shouldnt be called')

    response = client.get('/res2')
    assert response.text == 'OK'

    client.put('/res2', status=405)

    @Resource2.register('/connect')
    def connect_(handler, request):
        return handler.app.name

    response = client.get('/connect')
    assert response.text == 'muffin'


def test_handler_func(app, client):
    """Test convert functions to Muffin's Handlers."""

    @app.register('/test')
    def test(request):
        return 'TEST PASSED'
    assert 'test' in app.router._routes

    response = client.get('/test')
    assert response.text == 'TEST PASSED'

    response = client.post('/test')
    assert response.text == 'TEST PASSED'

    @app.register('/test1', methods='get')
    def test1(request):
        return 'TEST PASSED'

    assert 'test1' in app.router._routes

    response = client.get('/test1')
    assert response.text == 'TEST PASSED'

    @app.register('/test2', methods=('get', 'post'))
    def test2(request):
        return 'TEST PASSED'

    assert 'test2' in app.router._routes
    assert 'test2.post' in app.router._routes

    @app.register('/test3', methods='*')
    def test3(request):
        return 'TEST PASSED'

    assert 'test3' in app.router._routes
    response = client.get('/test3')
    assert response.status_code == 200

    response = client.post('/test3')
    assert response.status_code == 200

    response = client.delete('/test3')
    assert response.status_code == 200


def test_deffered(client, app):

    class Resource3(muffin.Handler):

        methods = 'get',

        def get(self, request):
            return 'Resource3'

    @Resource3.register('/dummy')
    def dummy(handler, request):
        return 'dummy here'

    app.register('/resource-3')(Resource3)

    response = client.get('/resource-3')
    assert response.text == 'Resource3'

    response = client.get('/dummy')
    assert response.text == 'dummy here'
