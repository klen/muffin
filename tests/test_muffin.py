import pytest
import muffin


@pytest.fixture(scope='session')
def app(loop):
    app = muffin.Application('muffin', loop=loop)

    @app.register(muffin.sre('/res(/{res})?/?'))
    class Resource(muffin.Handler):

        def get(self, request):
            return request.match_info

        def post(self, request):
            data = yield from self.parse(request)
            return data

    return app


def test_app(app):
    assert app.name == 'muffin'
    assert app.cfg


def test_sre():
    re = muffin.sre('/test/{id:\d+}/?')
    assert re.match('/test/1')
    assert re.match('/test/2/')

    re = muffin.sre('/test/{id:\d+}/{name}/?')
    assert re.match('/test/1/Mike')

    re = muffin.sre('/test(/{id}/?)?')
    assert re.match('/test/1')
    assert re.match('/test/1/').group('id') == '1'


def test_handler(app, client):
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


def test_manage(app, capsys):
    @app.manage.command
    def hello(name, lower=False):
        if lower:
            name = name.lower()
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.manage('example.app:app hello'.split())
    out, err = capsys.readouterr()
    assert not out
    assert err

    with pytest.raises(SystemExit):
        app.manage('example.app:app hello Mike'.split())
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.manage('example.app:app hello Sam --lower'.split())
    out, err = capsys.readouterr()
    assert "hello sam\n" == out


def test_signature():
    assert muffin.utils.create_signature('secret', 'message')


def test_password_hash():
    pwhash = muffin.utils.generate_password_hash('pass')
    assert pwhash

    assert not muffin.utils.check_password_hash('wrong', pwhash)
    assert muffin.utils.check_password_hash('pass', pwhash)
