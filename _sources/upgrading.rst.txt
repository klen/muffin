Upgrading
=========

This page lists behavior that changed in 3.x and tends to break working code on
an upgrade. The authoritative list is `CHANGELOG.md
<https://github.com/klen/muffin/blob/develop/CHANGELOG.md>`_; install a version
you tested and read the entries between the two versions before deploying.

Python support
--------------

Python 3.10 is no longer supported; the minimum is 3.11.

Async backend is a choice
-------------------------

asyncio is the default backend. trio and curio still work, but only when selected
for the process with ``--aiolib`` or ``MUFFIN_AIOLIB``. Code that relied on the
first installed library winning has to say which one it wants. See
:doc:`async`.

Handler methods
---------------

Class-based handlers no longer detect methods from the defined coroutines. A
handler now declares what it serves:

.. code-block:: python

    class ItemHandler(Handler):
        methods = ["get", "post"]        # required, or inherited from a parent

        async def get(self, request):
            ...

Declaring a method without implementing it fails when the class is defined, not
on the first request. A handler with no ``methods`` accepts every HTTP method at
the routing layer and then fails with a logged 500 for the ones it does not
implement, so listing them is not optional in practice.

Plugin options and environment
------------------------------

Environment variables now override plugin options, matching the application's own
precedence: keyword arguments passed to the plugin are defaults. A deployment that
set something like ``APP_PLUGIN_TIMEOUT`` and also passed ``timeout=`` in code
will get the environment value now, where the code used to win. The full order is
in :doc:`configuration`.

Disabled plugins
----------------

A plugin disabled by configuration is no longer half-attached: it is not added to
``app.plugins`` and its ``app`` property raises
:class:`~muffin.plugins.PluginNotInstalledError`. Code that guarded with
``plugin.app`` (or ignored the config) needs to check whether the plugin is
registered.

Forms
-----

``request.form()`` takes ``max_size`` only; ``file_memory_limit`` is gone. Uploads
stream to disk through ``upload_to``.

Background tasks and CLI
------------------------

Failed background tasks are logged instead of tearing down the connection, so
exceptions that used to surface in logs as request errors are now separate
entries. The CLI rejects unknown arguments instead of ignoring them, and the
``Manager.command`` alias is removed in favor of ``app.manage``.

Checking an upgrade
-------------------

.. code-block:: console

  $ pip install -U muffin
  $ pytest -xs                     # your suite, on every backend you support
  $ muffin your.module --help      # commands and options still resolve

If the app imports but behaves differently, the usual suspects are handler
``methods``, plugin option precedence and any code that assumed trio or curio was
the running backend.
