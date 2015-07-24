import pytest


@pytest.mark.async
def test_async():
    from aiohttp import request
    response = yield from request('GET', 'http://google.com')
    text = yield from response.text()
    assert 'html' in text


def test_client(app, client):

    @app.register('/client')
    def handler(request):
        return 'RESPONSE'

    response = client.get('/client')
    assert response.text == 'RESPONSE'


def test_pytest(loop):
    import asyncio

    assert asyncio.get_event_loop() is loop
