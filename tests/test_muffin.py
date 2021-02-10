"""Base Tests."""

from pathlib import Path
from unittest import mock

from asgi_lifespan import LifespanManager


def test_imports():
    import muffin

    assert muffin.Request
    assert muffin.Response
    assert muffin.ResponseError
    assert muffin.ResponseFile
    assert muffin.ResponseHTML
    assert muffin.ResponseJSON
    assert muffin.ResponseRedirect
    assert muffin.ResponseStream
    assert muffin.ResponseText
    assert muffin.ASGINotFound
    assert muffin.ASGIMethodNotAllowed
    assert muffin.TestClient


def test_app(app):
    assert app
    assert app.name == 'muffin'
    assert repr(app) == '<muffin.Application: muffin>'


def test_app_config():
    import muffin
    import os

    os.environ['TEST_DEBUG'] = 'true'

    app = muffin.Application('test', 'tests.appcfg', CONFIG='unknown')
    assert app.cfg
    assert app.cfg.STATIC_URL_PREFIX == '/static'
    assert app.cfg.CONFIG == 'tests.appcfg'
    assert app.cfg.CONFIG_VARIABLE == 42
    assert app.cfg.DEBUG is True


async def test_routing(app, client):

    @app.route('/simple', '/simple/(a|b|c)/?', methods=['GET'])
    async def test(request):
        return 200, 'simple'

    @app.route('/parameters/{param1}(/{param2})?')
    async def test(request):
        return 200, request.path_params

    res = await client.get('/simple')
    assert res.status_code == 200
    assert await res.text() == 'simple'

    res = await client.post('/404')
    assert res.status_code == 404

    res = await client.post('/simple')
    assert res.status_code == 405

    res = await client.get('/simple/a')
    assert res.status_code == 200
    assert await res.text() == 'simple'

    res = await client.get('/simple/b/')
    assert res.status_code == 200
    assert await res.text() == 'simple'

    res = await client.get('/parameters/42')
    assert res.status_code == 200
    assert await res.json() == {'param1': '42', 'param2': ''}

    res = await client.get('/parameters/42/33')
    assert res.status_code == 200
    assert await res.json() == {'param1': '42', 'param2': '33'}


async def test_responses(app, client):

    @app.route('/none')
    async def none(request):
        return None

    @app.route('/bool')
    async def none(request):
        return False

    @app.route('/str')
    async def str(request):
        return 'str'

    @app.route('/bytes')
    async def bytes(request):
        return b'bytes'

    @app.route('/json')
    async def json(request):
        return {'test': 'passed'}

    res = await client.get('/none')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert await res.json() is None

    res = await client.get('/bool')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert await res.json() is False

    res = await client.get('/str')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'text/html; charset=utf-8'
    assert await res.text() == 'str'

    res = await client.get('/bytes')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'text/html; charset=utf-8'
    assert await res.text() == 'bytes'

    res = await client.get('/json')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert await res.json() == {'test': 'passed'}


async def test_websockets(app, client):
    from muffin import ResponseWebSocket

    @app.route('/stream')
    async def stream(request):
        ws = ResponseWebSocket(request)
        await ws.accept()
        msg = await ws.receive()
        assert msg == 'ping'
        await ws.send('pong')
        await ws.close()

    async with client.websocket('/stream') as ws:
        await ws.send('ping')
        msg = await ws.receive()
        assert msg == 'pong'


async def test_middlewares(app, client):

    @app.middleware
    async def simple_middleware(app, request, receive, send):
        response = await app(request, receive, send)

        if request.path == '/md/simple':
            response.headers['x-simple'] = 'passed'

        return response

    @app.middleware
    def classic_middleware(app):
        async def middleware(scope, receive, send):
            async def custom_send(msg):
                if scope['path'] == '/md/classic' and msg['type'] == 'http.response.start':
                    msg['headers'].append((b'x-classic', b'passed'))
                await send(msg)

            await app(scope, receive, custom_send)

        return middleware

    @app.route('/md/simple')
    async def simple(request):
        return 200,

    @app.route('/md/classic')
    async def classic(request):
        return 200,

    res = await client.get('/')
    assert res.status_code == 200
    assert not res.headers.get('x-simple')
    assert not res.headers.get('x-classic')

    res = await client.get('/md/simple')
    assert res.status_code == 200
    assert res.headers['x-simple'] == 'passed'
    assert not res.headers.get('x-classic')

    res = await client.get('/md/classic')
    assert res.status_code == 200
    assert not res.headers.get('x-simple')
    assert res.headers['x-classic'] == 'passed'


async def test_lifespan(app, anyio_backend):
    import muffin

    start, finish = mock.MagicMock(), mock.MagicMock()

    app.on_startup(start)
    app.on_shutdown(finish)

    async with LifespanManager(app):
        assert start.called
        assert not finish.called

        client = muffin.TestClient(app)
        res = await client.get('/')
        assert res.status_code == 200

    assert start.called
    assert finish.called


def test_configure_logging():
    import muffin

    dummy = {'dummy': 'dict', 'version': 1}
    with mock.patch('logging.config.dictConfig') as mocked:
        app = muffin.Application('muffin', LOG_CONFIG=dummy)
        assert app.logger
        assert app.logger.handlers
    mocked.assert_called_once_with(dummy)


async def test_static_folders(anyio_backend):
    import muffin

    app = muffin.Application(
        'test',
        static_folders=['tests', Path('__file__').parent.parent],
        static_url_prefix='/assets')
    assert app.cfg.STATIC_FOLDERS
    assert app.cfg.STATIC_URL_PREFIX == '/assets'

    @app.route('/')
    async def index(request):
        return 'OK'

    client = muffin.TestClient(app)
    res = await client.get('/')
    assert res.status_code == 200

    res = await client.get('/assets/test_muffin.py')
    assert res.status_code == 200
    text = await res.text()
    assert text.startswith('"""Base Tests."""')

    res = await client.get('/assets/setup.cfg')
    assert res.status_code == 200


async def test_error_handlers(client, app):
    import muffin

    @app.route('/500')
    async def raise_500(request):
        raise muffin.ResponseError(500)

    @app.route('/unhandled')
    async def raise_unhandled(request):
        raise Exception()

    @app.on_error(muffin.ResponseError)
    async def handler(exc):
        return 'Custom Server Error'

    @app.on_error(404)
    async def handler_404(exc):
        return 'Custom 404'

    @app.on_error(Exception)
    async def handle_exception(exc):
        return 'Custom Unhandled'

    assert app.exception_handlers

    res = await client.get('/unhandled')
    assert res.status_code == 200
    assert await res.text() == 'Custom Unhandled'

    res = await client.get('/500')
    assert res.status_code == 200
    assert await res.text() == 'Custom Server Error'

    res = await client.get('/404')
    assert res.status_code == 200
    assert await res.text() == 'Custom 404'
