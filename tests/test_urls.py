import asyncio


def test_raw_route():
    from muffin.urls import RawReRoute

    @asyncio.coroutine
    def handler(request):
        return 'OK'

    route = RawReRoute('GET', handler, 'test', '/foo/bar/?')
    assert route.url() == '/foo/bar'

    route = RawReRoute('GET', handler, 'test', '/foo/(?P<bar>\d+)(/(?P<foo>\w+))?/?')
    assert route.url() == '/foo/0'
    assert route.url(10) == '/foo/10'
    assert route.url(bar=11) == '/foo/11'
    assert route.url(foo=12) == '/foo/0/12'
    assert route.url(bar=13, foo=14) == '/foo/13/14'
    assert route.url(bar=13, foo=14, query={'a': 'b'}) == '/foo/13/14?a=b'


def test_parse():
    from muffin.urls import parse, RETYPE

    assert isinstance(parse('/'), str)
    assert isinstance(parse('/test.jpg'), str)
    assert isinstance(parse('/{foo}/'), str)
    assert isinstance(parse('/{foo:\d+}/'), RETYPE)
    assert isinstance(parse('/{foo}/?'), RETYPE)
