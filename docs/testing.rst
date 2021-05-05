Testing
========

TestClient
----------

The test client allows you to make requests against your ASGI application.

.. code-block:: python

    from muffin import Application, TestClient, ResponseWebSocket

    app = Application()

    # Test HTTP requests
    @app.route('/')
    async def home(request):
        return "OK"

    client = TestClient(app)
    response = await client.get('/')
    assert response.status_code == 200
    assert await response.text() == 'OK'

    # Test Websockets
    @app.route('/ws')
    async def socket(request):
        ws = ResponseWebSocket(request)
        async with ws:
            msg = await ws.receive()
            if msg == 'ping':
                await ws.send('pong')

    async with client.websocket('/ws') as ws:
        await ws.send('ping')
        msg = await ws.receive()
        assert msg == 'pong'

Check the TestClient API Reference: :class:`~muffin.TestClient`


Pytest Support
--------------

Set module path to your Muffin Application in pytest configuration file or use
command line option ``--muffin-app``.

Example: ::

    $ py.test -xs --muffin-app example

After that the fixtures ``app``, ``client`` will be available for your tests.

.. warning::

   if you get a warning from pytest: ``"PytestCollectionWarning: cannot collect test class 'ASGITestClient'``
   change TestClient import ``from muffin import TestClient as Client``
