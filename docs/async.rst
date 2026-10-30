Async libraries
===============

Muffin speaks ASGI, so the framework itself does not care which event loop runs
it: asyncio, trio and curio all work. What does require a choice is every piece
of code that *starts* a loop: the CLI, scripts, tests and background tooling.

Selecting a backend
-------------------

asyncio is the default. Override it for a process with the ``MUFFIN_AIOLIB``
environment variable, or per command with the CLI option:

.. code-block:: console

  $ MUFFIN_AIOLIB=trio muffin app run
  $ muffin app --aiolib curio cleanup

Installed libraries are detected at import time. ``--aiolib`` only appears in
``muffin app --help`` when more than one of them is importable.

Running coroutines from sync code
---------------------------------

``aio_run`` runs a coroutine on the selected backend, the same way the CLI does:

.. code-block:: python

    from muffin.utils import aio_run

    async def main():
        ...

    aio_run(main)

Inside a coroutine, ``current_async_library()`` reports the backend that is
actually running:

.. code-block:: python

    from muffin.utils import current_async_library

    async def main():
        assert current_async_library() in {"asyncio", "trio", "curio"}

One process, one backend
------------------------

The choice is cached in the process the first time a loop is started, so the
first call wins: set ``MUFFIN_AIOLIB`` (or ``--aiolib``) before anything runs a
loop. Starting a second loop on another backend in the same process does not
switch backends; it silently keeps the first one.

That is why tests parametrize the backend instead of switching at runtime. See
:doc:`testing`.

Writing backend-agnostic code
-----------------------------

Handlers, plugins and helpers should avoid ``asyncio``-only APIs: ``asyncio.sleep``,
``asyncio.create_task`` and ``asyncio.Queue`` do not exist in trio or curio. If
the code has to run on all three, keep such calls behind plugin code that ships
its own compat layer (the shipped plugins do), or pick a single backend for the
project and say so in its README.

uvloop
------

Under asyncio, uvicorn can install uvloop as the event loop policy; Muffin needs
no changes for that:

.. code-block:: console

  $ pip install "uvicorn[standard]"
  $ uvicorn app:app --loop uvloop

:doc:`deploy` covers the rest of the server setup.
