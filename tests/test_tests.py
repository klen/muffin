import pytest
import asyncio


@pytest.mark.async
def test_async():
    yield from asyncio.sleep(.1)
    assert True


def test_client(app, client):

    @app.register('/client')
    def handler(request):
        return 'RESPONSE'

    response = client.get('/client')
    assert response.text == 'RESPONSE'


def test_pytest(loop):
    import asyncio

    assert asyncio.get_event_loop() is loop
