from unittest.mock import patch

import pytest

import muffin


def test_app(app):
    assert app.name == 'muffin'
    assert app.cfg

    with pytest.raises(AttributeError):
        app.local

    with pytest.raises(RuntimeError):
        app.cfg.OPTION = 42

    with pytest.raises(RuntimeError):
        app.ps.PLUGIN = 42


def test_app_logging_cfg():
    dummy = {'dummy': 'dict'}
    with patch('logging.config.dictConfig') as m:
        muffin.Application(
            'muffin',
            LOGGING=dummy
        )
    m.assert_called_once_with(dummy)


def test_view(app, client):

    @app.register
    def view(request):
        return 'VIEW'

    response = client.get('/view')
    assert response.text == 'VIEW'


def test_str(app, client):

    @app.register('/str')
    def str(request):
        return 'STR'

    response = client.get('/str')
    assert response.text == 'STR'


def test_bytes(app, client):

    @app.register('/bytes')
    def bytes(request):
        return b'BYTES'

    response = client.get('/bytes')
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert response.text == 'BYTES'


def test_custom_methods(app, client):

    @app.register('/caldav', methods='PROPFIND')
    def propfind(request):
        return b'PROPFIND'

    response = client.request('/caldav', method='PROPFIND')
    assert response.text == 'PROPFIND'


def test_static(app, client):
    assert app.cfg.STATIC_FOLDERS == [
        'tests/static1',
        'tests/static2',
    ]
    response = client.get('/static/file1')
    assert response.status_code == 200
    response = client.get('/static/file2')
    assert response.status_code == 200


def test_manage(app, capsys):
    @app.manage.command
    def hello(name, lower=False):
        if lower:
            name = name.lower()
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.manage(*'hello'.split())
    out, err = capsys.readouterr()
    assert not out
    assert err

    with pytest.raises(SystemExit):
        app.manage(*'hello Mike'.split())
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.manage(*'hello Sam --lower'.split())
    out, err = capsys.readouterr()
    assert "hello sam\n" == out


def test_signature():
    assert muffin.utils.create_signature('secret', 'message')


def test_password_hash():
    pwhash = muffin.utils.generate_password_hash('pass')
    assert pwhash

    assert not muffin.utils.check_password_hash('wrong', pwhash)
    assert muffin.utils.check_password_hash('pass', pwhash)


def test_error_pages(client, loop, app):

    @app.register(muffin.HTTPNotFound)
    def handle_404(request):
        return muffin.Response(text='Muffin 404', status=404)

    @app.register(Exception)
    def handle_500(request):
        return muffin.Response(text='Muffin 500')

    @app.register('/500')
    def raise_500(request):
        raise Exception('Unknow exception.')

    loop.run_until_complete(app.start())

    response = client.get('/404', status=404)
    assert 'Muffin 404' == response.text

    response = client.get('/500')
    assert response.text == 'Muffin 500'

    @app.register('/400')
    def raise_400(request):
        raise muffin.HTTPBadRequest()

    @app.register(muffin.HTTPBadRequest)
    def handle_400(request):
        return muffin.Response(text='Muffin 400', status=400)

    response = client.get('/400', status=400)
    assert 'Muffin 400' == response.text
