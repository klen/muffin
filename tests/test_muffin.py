import pytest

import muffin


@pytest.mark.async
def test_async():
    from aiohttp import request
    response = yield from request('GET', 'http://google.com')
    text = yield from response.text()
    assert 'html' in text


def test_pytest(loop):
    import asyncio

    assert asyncio.get_event_loop() == loop


def test_app(app):
    assert app.name == 'muffin'
    assert app.cfg


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


def test_static(app, client):
    assert app.cfg.STATIC_FOLDERS == [
        'tests/static1',
        'tests/static2',
    ]
    response = client.get('/static/file1')
    assert response.status_code == 200
    response = client.get('/static/file2')
    assert response.status_code == 200


def test_sre():
    re = muffin.sre('/test/{id:\d+}/?')
    assert re.match('/test/1')
    assert re.match('/test/2/')

    re = muffin.sre('/test/{id:\d+}/{name}/?')
    assert re.match('/test/1/Mike')

    re = muffin.sre('/test(/{id}/?)?')
    assert re.match('/test/1')
    assert re.match('/test/1/').group('id') == '1'


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


def test_error_pages(client, loop, app):

    def handle_404(request):
        return muffin.Response(text='Muffin 404', status=404)

    app.register_error(muffin.HTTPNotFound, handle_404)

    loop.run_until_complete(app.start())

    response = client.get('/404', status=404)
    assert 'Muffin 404' == response.text

    @app.register('/400')
    def raise_400(request):
        raise muffin.HTTPBadRequest()

    @app.register_error(muffin.HTTPBadRequest)
    def handle_400(request):
        return muffin.Response(text='Muffin 400', status=400)

    response = client.get('/400', status=400)
    assert 'Muffin 400' == response.text

    @app.register('/500', muffin.HTTPInternalServerError)
    def handle_500(request):
        return muffin.Response(text='Muffin 500', status=500)

    @app.register('/raise500')
    def raise_500(request):
        raise muffin.HTTPInternalServerError()

    response = client.get('/500', status=500)
    assert 'Muffin 500' == response.text

    response = client.get('/raise500', status=500)
    assert 'Muffin 500' == response.text
