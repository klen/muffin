import asyncio


def test_raw_route():
    from muffin.urls import RawReResource

    resource = RawReResource('/foo/bar/?', 'test')
    assert resource.url() == '/foo/bar'

    resource = RawReResource('/foo/(?P<bar>\d+)(/(?P<foo>\w+))?/?', 'test')
    assert resource.url() == '/foo/0'
    assert resource.url(10) == '/foo/10'
    assert resource.url(bar=11) == '/foo/11'
    assert resource.url(foo=12) == '/foo/0/12'
    assert resource.url(bar=13, foo=14) == '/foo/13/14'
    assert resource.url(bar=13, foo=14, query={'a': 'b'}) == '/foo/13/14?a=b'


def test_parse():
    from muffin.urls import parse, RETYPE

    assert isinstance(parse('/'), str)
    assert isinstance(parse('/test.jpg'), str)
    assert isinstance(parse('/{foo}/'), str)
    assert isinstance(parse('/{foo:\d+}/'), RETYPE)
    assert isinstance(parse('/{foo}/?'), RETYPE)


def test_parent(loop):
    from muffin.urls import ParentResource

    parent = ParentResource('/api/', name='api')
    resource = parent.add_resource('/test/', name='test')

    @asyncio.coroutine
    def handler(request):
        return 'TEST PASSED.'

    resource.add_route('*', handler)
    info, _ = loop.run_until_complete(parent.resolve('GET', '/api/test/'))
    assert info is not None

    result = loop.run_until_complete(info.handler(None))
    assert result == 'TEST PASSED.'

    assert parent.url() == '/api/'
    assert parent.url(name='test') == '/api/test/'


def test_register_url(app):
    from muffin.urls import routes_register

    def handler():
        pass

    routes_register(app, handler,
                    '/path/{id:\d+}', '/path/add', '/other/path',
                    name='handler')
    assert 'handler' in app.router
    assert 'handler2' in app.router
    assert 'handler3' in app.router
