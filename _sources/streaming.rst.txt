Streaming, SSE and WebSockets
=============================

Streams
-------

:class:`~muffin.ResponseStream` takes an async generator and sends each chunk as
it is produced. Return it from a handler; nothing gets buffered:

.. code-block:: python

    from muffin import ResponseStream

    @app.route("/export")
    async def export(request):
        async def rows():
            async for row in fetch_rows():
                yield f"{row.id}\t{row.name}\n"

        return ResponseStream(rows(), headers={
            "Content-Type": "text/tab-separated-values",
            "Content-Disposition": 'attachment; filename="export.tsv"',
        })

Cleanup belongs in ``finally`` inside the generator, because the client can go
away in the middle of a stream:

.. code-block:: python

    async def rows():
        cursor = await db.cursor()
        try:
            async for row in cursor:
                yield format_row(row)
        finally:
            await cursor.close()

Server-Sent Events
------------------

:class:`~muffin.ResponseSSE` is a stream with the ``text/event-stream`` content
type and the framing SSE requires. Yield strings or dicts; dicts are rendered as
``field: value`` lines, and every event is terminated by a blank line:

.. code-block:: python

    from muffin import ResponseSSE

    @app.route("/events")
    async def events(request):
        async def ticks():
            while True:
                await sleep(1)
                yield {"event": "tick", "data": now()}   # event: tick\ndata: ...\n\n

        return ResponseSSE(ticks())

The response sets ``Cache-Control: no-cache``; send a blank line with a comment
(``": keep-alive"``) if proxies need it.

Files
-----

:class:`~muffin.ResponseFile` streams a file from disk and sets
``Content-Disposition`` when ``filename`` is given:

.. code-block:: python

    from muffin import ResponseFile

    @app.route("/download/{name}")
    async def download(request):
        name = request.path_params["name"]
        return ResponseFile(f"uploads/{name}", filename=name)

Under asyncio, file streaming needs the optional ``aiofile`` package:
``pip install aiofile``.

WebSockets
----------

A websocket handler owns the connection for as long as it is open:

.. code-block:: python

    from muffin import ASGIConnectionClosedError, ResponseWebSocket

    @app.route("/ws")
    async def ws(request):
        async with ResponseWebSocket(request) as socket:
            try:
                while True:
                    message = await socket.receive()
                    await socket.send(f"echo: {message}")
            except ASGIConnectionClosedError:
                return   # normal disconnect, nothing to log

``receive()`` raises :class:`~muffin.ASGIConnectionClosedError` when the client
closes the connection or the server shuts down. Catch it where the handler loop
lives; letting it escape produces a logged error for a case that is not an error.
HTTP and websocket routes live in the same application; the ASGI server decides
which protocol a connection uses.

Testing streams
---------------

The test client reads the whole stream, so streaming handlers are tested like
regular ones:

.. code-block:: python

    async def test_export(client):
        response = await client.get("/export")
        assert response.status_code == 200
        assert await response.text() == "1\tone\n"

For websockets use ``client.websocket()``; see :doc:`testing`.
