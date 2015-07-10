import muffin


def test_handler(app, client):

    @app.register('/test', methods='get')
    def test(request):
        return 'TEST PASSED'

    assert 'test-get' in app.router._routes
    assert 'test-post' not in app.router._routes

    response = client.get('/test')
    assert response.text == 'TEST PASSED'

    @app.register('/test2', methods=('get', 'post'))
    def test2(request):
        return 'TEST PASSED'

    assert 'test2-get' in app.router._routes
    assert 'test2-post' in app.router._routes

    @app.register('/test3', methods='*')
    def test3(request):
        return 'TEST PASSED'

    assert 'test3-*' in app.router._routes
    response = client.get('/test3')
    assert response.status_code == 200

    response = client.post('/test3')
    assert response.status_code == 200

    response = client.delete('/test3')
    assert response.status_code == 200

    @app.register(muffin.sre('/res(/{res})?/?'))
    class Resource(muffin.Handler):

        def get(self, request):
            return request.match_info

        def post(self, request):
            data = yield from self.parse(request)
            return dict(data)

    assert set(Resource.methods) == set(['GET', 'POST'])

    assert 'resource-*' in app.router._routes

    response = client.delete('/res', status=405)

    response = client.get('/res')
    assert response.json == {'res': None}

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
