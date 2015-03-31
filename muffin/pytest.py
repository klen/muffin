# Configure your tests here
import asyncio
import os

import pytest
import webtest
from aiohttp.multidict import CIMultiDict
from aiohttp.protocol import HttpVersion11, HttpVersion10, RawRequestMessage
from aiohttp.streams import StreamReader
from aiohttp.web import (
    AbstractMatchInfo,
    HTTPException,
    Request,
    RequestHandler,
    RequestHandlerFactory,
    StreamResponse,
)
from gunicorn import util


class TestRequestHandler(RequestHandler):

    @asyncio.coroutine
    def handle_request(self, message, payload):
        app = self._app

        request = Request(app, message, payload, self.transport, self.reader, self.writer)

        request._writer = lambda: None # noqa
        request._writer.write = lambda b: None # noqa

        try:
            match_info = yield from self._router.resolve(request)

            assert isinstance(match_info, AbstractMatchInfo), match_info

            request._match_info = match_info
            handler = match_info.handler

            for factory in reversed(self._middlewares):
                handler = yield from factory(app, handler)
            resp = yield from handler(request)

            if not isinstance(resp, StreamResponse):
                raise RuntimeError(
                    ("Handler {!r} should return response instance, "
                     "got {!r} [middlewares {!r}]").format(
                         match_info.handler,
                         type(resp),
                         self._middlewares))
        except HTTPException as exc:
            resp = exc

        return resp


class TestRequest(webtest.TestRequest):

    """ Support asyncio loop. """

    def call_application(self, application, catch_exc_info=False):
        if self.is_body_seekable:
            self.body_file_raw.seek(0)

        http_version = HttpVersion10 if self.http_version == 'HTTP/1.0' else HttpVersion11
        message = RawRequestMessage(
            self.method, self.path_qs, http_version, CIMultiDict(self.headers), False, False)
        payload = StreamReader(loop=application.loop)
        payload.feed_data(self.body_file_raw.read())
        payload.feed_eof()

        loop = asyncio.get_event_loop()
        handler = RequestHandlerFactory(
            application, application.router, handler=TestRequestHandler, loop=loop)()
        response = loop.run_until_complete(handler.handle_request(message, payload))

        headers = dict(response.headers)
        for cookie in response.cookies.values():
            headers['SET-COOKIE'] = cookie.OutputString()

        return response.status, headers.items(), [response._body], None


class TestApp(webtest.TestApp):

    RequestClass = TestRequest


def pytest_addoption(parser):
    """ Add MUFFIN testing options. """

    parser.addini('muffin_app', 'Set path to muffin application')
    parser.addoption('--muffin-app', dest='muffin_app', help='Set to muffin application')

    parser.addini('muffin_config', 'Set module path to muffin configuration')
    parser.addoption('--muffin-config', dest='muffin_config',
                     help='Set module path to muffin configuration')


def pytest_load_initial_conftests(early_config, parser, args):
    from muffin import CONFIGURATION_ENVIRON_VARIABLE
    options = parser.parse_known_args(args)

    # Initialize configuration
    config = options.muffin_config or early_config.getini('muffin_config')
    if config:
        os.environ[CONFIGURATION_ENVIRON_VARIABLE] = config

    # Initialize application
    app = options.muffin_app or early_config.getini('muffin_app')
    early_config.app = app


@pytest.fixture(scope='session')
def loop(request):
    """ Create and provide asyncio loop. """
    loop = asyncio.new_event_loop()
    request.addfinalizer(lambda: loop.close())
    return loop


@pytest.fixture(scope='session')
def app(pytestconfig, loop, request):
    """ Provide an example application. """
    app = pytestconfig.app
    if not app:
        raise SystemExit(
            'Improperly configured. Please set ``muffin_app`` in your pytest config. '
            'Or use ``--muffin-app`` command option.')
    app = util.import_app(app)

    return app


@pytest.fixture(scope='session', autouse=True)
def _initialize(app, loop, request):
    app._loop = loop
    loop.run_until_complete(app.start())

    if 'peewee' in app.plugins:
        import peewee

        for model in app.plugins.peewee.models.values():
            try:
                model.create_table()
            except peewee.OperationalError:
                pass

    @request.addfinalizer
    def finish():
        loop.run_until_complete(app.finish())


@pytest.fixture(scope='function')
def client(app):
    """ Prepare a tests' client. """
    client = TestApp(app, lint=False)
    client.exception = webtest.AppError
    return client


@pytest.fixture(scope='function')
def db(app, request):
    """ Run tests in transaction. """
    if 'peewee' in app.plugins:
        app.ps.peewee.database.set_autocommit(False)
        app.ps.peewee.database.begin()
        request.addfinalizer(lambda: app.ps.peewee.database.rollback())
        return app.ps.peewee.database


@pytest.fixture(scope='session')
def mixer(app):
    if 'peewee' in app.plugins:
        from mixer.backend.peewee import Mixer
        return Mixer(commit=True)
