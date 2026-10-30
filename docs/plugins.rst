.. include:: ../README.rst
    :start-after: .. _plugins:
    :end-before: .. _benchmarks:

Writing a plugin
----------------

A plugin is a class derived from :class:`muffin.plugins.BasePlugin`. It gets a
configuration of its own, access to the application, and hooks that run with the
application lifespan:

.. code-block:: python

    from muffin.plugins import BasePlugin


    class Plugin(BasePlugin):
        name = "mailer"                                  # config prefix and app.plugins key
        defaults = {"disabled": False, "host": "localhost"}

        async def startup(self):
            self.client = Client(self.cfg.host)

        async def shutdown(self):
            await self.client.close()

        async def send(self, to, subject):
            await self.client.send(to, subject)

Register it with the application:

.. code-block:: python

    plugin = Plugin(app)
    await plugin.send("user@example.com", "Hello")

``Plugin(app)`` binds the plugin, configures it, registers it in ``app.plugins``
and hooks ``startup``/``shutdown`` into the application lifespan. Binding is
skipped, with a warning in the log, when the resolved config has ``disabled``
set. Pass ``name=`` to register a second instance of the same plugin type:

.. code-block:: python

    primary = Plugin(app, name="mailer_primary")
    secondary = Plugin(app, name="mailer_secondary")

Options are resolved in this order: ``defaults``, application config keys with
the ``{name}_`` prefix, keyword arguments, then environment variables
``{APP_NAME}_{NAME}_{OPTION}``. Details are in :doc:`configuration`.

A plugin may also provide request middleware by setting ``middleware`` to a
callable; it is registered with ``app.middleware``:

.. code-block:: python

    class Plugin(BasePlugin):
        name = "timing"

        async def middleware(self, app, request, receive, send):
            response = await app(request, receive, send)
            if response is not None:
                response.headers["x-powered-by"] = "muffin"
            return response

The plugin is usable outside a request, for example in CLI commands or tests:

.. code-block:: python

    async with plugin:                     # calls startup/shutdown
        await plugin.send("user@example.com", "Hello")

    await plugin.restart()                 # shutdown, then startup again

Tests get plugin startup for free: the pytest ``app`` fixture runs the
application lifespan, which awaits every plugin's ``startup`` before yielding
the application. See :doc:`testing`.

What ``setup()`` does
---------------------

Binding is done by ``setup(app, **options)``, which is what ``Plugin(app)`` calls.
It returns ``True`` when the plugin is registered and ``False`` when the resolved
configuration disables it. On a disabled plugin nothing is attached: it is not in
``app.plugins``, its lifespan hooks are not registered, and touching ``plugin.app``
raises :class:`~muffin.plugins.PluginNotInstalledError`. Code that may run with a
disabled plugin should check the return value or ``app.plugins``.

``setup()`` also accepts ``name=`` to register a second instance of the same
plugin type, which is how a project uses one plugin twice (two databases, two
mailers).

Errors
------

.. autoclass:: muffin.plugins.PluginError

.. autoclass:: muffin.plugins.PluginNotInstalledError

Both live in ``muffin.plugins``. ``PluginError`` is the base class for plugin
failures, so plugin code can raise it instead of inventing a hierarchy;
``PluginNotInstalledError`` is a ``RuntimeError`` for the programming error of
using a plugin that was never bound.

Publishing a plugin
-------------------

A plugin is a normal Python package. Keep the conventions the ecosystem uses:
name the distribution ``muffin-<name>``, expose ``Plugin`` from the package root,
let ``Plugin(app)`` work with no extra calls, and make configuration overridable
from ``{APP}_{PLUGIN}_*`` environment variables by reading ``self.cfg`` instead of
os.environ. A plugin's own tests can use the pytest ``app`` fixture from the host
application, or instantiate the plugin in a test application directly.
