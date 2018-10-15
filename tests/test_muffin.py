from unittest.mock import patch

import pytest

import muffin


async def test_app(app):
    assert app.name == 'muffin'
    assert app.cfg

    app.on_startup.freeze()
    await app.startup()
    app.freeze()

    with pytest.raises(AttributeError):
        app.local

    with pytest.raises(RuntimeError):
        app.cfg.OPTION = 42

    with pytest.raises(RuntimeError):
        app.ps.PLUGIN = 42


def test_app_logging_cfg():
    dummy = {'dummy': 'dict'}
    with patch('logging.config.dictConfig') as m:
        muffin.Application('muffin', LOGGING=dummy)
    m.assert_called_once_with(dummy)


async def test_static(aiohttp_client):
    app = muffin.Application('test', STATIC_FOLDERS=[
        'tests/static1',
        'tests/static2',
    ])
    client = await aiohttp_client(app)

    resp = await client.get('/static/file1')
    assert resp.status == 200
    body = await resp.read()
    assert body == b'content1\n'

    resp = await client.get('/static/file2')
    assert resp.status == 200
    body = await resp.read()
    assert body == b'content2\n'


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


async def test_error_pages(aiohttp_client):

    app = muffin.Application('test')

    @app.register('/400')
    def raise_400(request):
        raise muffin.HTTPBadRequest()

    @app.register(muffin.HTTPBadRequest)
    def handle_400(request):
        return muffin.Response(text='Custom 400', status=400)

    @app.register(muffin.HTTPNotFound)
    def handle_404(request):
        return muffin.Response(text='Custom 404', status=404)

    @app.register(Exception)
    def handle_500(request):
        return muffin.Response(text='Custom 500')

    @app.register('/500')
    def raise_500(request):
        raise Exception('Unknow exception.')

    client = await aiohttp_client(app)

    async with client.get('/400') as resp:
        assert resp.status == 400
        text = await resp.text()
        assert text == 'Custom 400'

    async with client.get('/404') as resp:
        assert resp.status == 404
        text = await resp.text()
        assert text == 'Custom 404'

    async with client.get('/500') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'Custom 500'
