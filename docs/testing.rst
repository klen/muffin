Testing
=======

Muffin provides a built-in test client for testing your application.

TestClient
----------

Use :class:`~muffin.TestClient` to test HTTP requests:

**Example application code:**

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.route('/')
    async def home(request):
        return "OK"

**Tests:**

.. code-block:: python

    from muffin import TestClient

    client = TestClient(app)

    response = await client.get('/')
    assert response.status_code == 200
    assert await response.text() == 'OK'


WebSocket Testing
-----------------

You can also test WebSocket routes:

.. code-block:: python

    from muffin import Application, ResponseWebSocket

    app = Application()

    @app.route('/ws')
    async def socket(request):
        async with ResponseWebSocket(request) as ws:
            msg = await ws.receive()
            if msg == 'ping':
                await ws.send('pong')

**Test WebSockets:**

.. code-block:: python

    from muffin import TestClient

    client = TestClient(app)

    async with client.websocket('/ws') as ws:
        await ws.send('ping')
        msg = await ws.receive()
        assert msg == 'pong'


Check the TestClient API Reference: :class:`~muffin.TestClient`


Pytest Integration
------------------

Muffin provides fixtures for integration with pytest.

**Setup:**

Set the module path to your Muffin application in your pytest configuration file or use the ``--muffin-app`` command-line option:

.. code-block:: console

    $ pytest -xs --muffin-app example

After this, the following fixtures will be available in your tests:

- ``app`` – your Muffin application
- ``client`` – a :class:`~muffin.TestClient` instance

.. warning::

   If you get the warning: ``PytestCollectionWarning: cannot collect test class 'ASGITestClient'``,
   change the TestClient import to: ``from muffin import TestClient as Client``
