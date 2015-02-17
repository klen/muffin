# Configure your tests here
import asyncio

import pytest
import webtest
from aiohttp.protocol import HttpVersion11, HttpVersion10, RawRequestMessage
from aiohttp.multidict import CIMultiDict
from aiohttp.web import (
    AbstractMatchInfo,
    HTTPException,
    Request,
    RequestHandler,
    RequestHandlerFactory,
    StreamResponse,
)


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
        payload = self.body_file_raw

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


@pytest.fixture(scope='session')
def app():
    """ Provide an example application. """
    from app import app

    try:
        import peewee
        import models

        for name in dir(models):
            cls = getattr(models, name)
            if isinstance(cls, type) and issubclass(cls, peewee.Model):
                try:
                    cls.create_table()
                except peewee.OperationalError:
                    pass

    except ImportError:
        pass

    return app


@pytest.fixture(scope='session')
def loop(request):
    """ Create and provide asyncio loop. """
    loop = asyncio.new_event_loop()
    request.addfinalizer(lambda: loop.close())
    return loop


@pytest.fixture(scope='function')
def client(app, loop):
    """ Prepare a tests' client. """
    client = TestApp(app, lint=False)
    client.exception = webtest.AppError
    return client


@pytest.fixture(scope='function')
def db(app, request):
    """ Run tests in transaction. """
    app.peewee.database.set_autocommit(False)
    app.peewee.database.begin()
    request.addfinalizer(lambda: app.peewee.database.rollback())
    return app.peewee.database


@pytest.fixture(scope='session')
def mixer(app):
    from mixer.backend.peewee import Mixer
    return Mixer(commit=True)
