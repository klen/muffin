import asyncio


def test_raw_route():
    from muffin.urls import RawReResource

    resource = RawReResource('/foo/bar/?', 'test')
    url = resource.url_for()
    assert resource.url_for().path == '/foo/bar'

    resource = RawReResource('/foo/(?P<bar>\d+)(/(?P<foo>\w+))?/?', 'test')
    assert resource.url_for().path == '/foo/0'
    assert resource.url_for(10).path == '/foo/10'
    assert resource.url_for(bar=11).path == '/foo/11'
    assert resource.url_for(foo=12).path == '/foo/0/12'
    assert resource.url_for(bar=13, foo=14).path == '/foo/13/14'
    assert str(resource.url_for(bar=13, foo=14).with_query({'a': 'b'})) == '/foo/13/14?a=b'


def test_parse():
    from muffin.urls import parse, RETYPE

    assert isinstance(parse('/'), str)
    assert isinstance(parse('/test.jpg'), str)
    assert isinstance(parse('/{foo}/'), str)
    assert isinstance(parse('/{foo:\d+}/'), RETYPE)
    assert isinstance(parse('/{foo}/?'), RETYPE)


#  def test_parent(loop):
    #  from muffin.urls import ParentResource

    #  parent = ParentResource('/api/', name='api')
    #  resource = parent.add_resource('/test/', name='test')

    #  @asyncio.coroutine
    #  def handler(request):
        #  return 'TEST PASSED.'

    #  resource.add_route('*', handler)
    #  info, _ = loop.run_until_complete(parent.resolve('GET', '/api/test/'))
    #  assert info is not None

    #  result = loop.run_until_complete(info.handler(None))
    #  assert result == 'TEST PASSED.'

    #  assert parent.url() == '/api/'
    #  assert parent.url(name='test') == '/api/test/'


def test_register_url(app):
    from muffin.urls import routes_register

    def handler():
        pass

    routes_register(app, handler, '/path/{id:\d+}', '/path/add', '/other/path', name='endpoint')

    assert 'endpoint' in app.router and str(app.router['endpoint'].url_for(id=5)) == '/path/5'
    assert 'endpoint2' in app.router and str(app.router['endpoint2'].url_for()) == '/path/add'
    assert 'endpoint3' in app.router and str(app.router['endpoint3'].url_for()) == '/other/path'
