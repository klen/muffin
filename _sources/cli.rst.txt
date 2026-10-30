CLI integration
===============

Muffin ships a ``muffin`` command that loads your application and calls commands
registered on it.

.. code-block:: console

    $ muffin path.to.your.module --help
    $ muffin path.to.your.module:app_object_name --help

The argument is an import path: either a module that exposes ``app`` or a dotted
path to the application object itself. The working directory is added to
``sys.path``, so the command works from the project root.

Global options:

- ``--config settings.local``: set ``MUFFIN_CONFIG`` before the app is imported
- ``--aiolib asyncio|trio|curio``: pick the async library for the command, shown
  only when more than one is installed
- ``--version``: print the Muffin version

Built-in commands
-----------------

run
~~~

Start the application with uvicorn. Host and port default to ``localhost`` and
``5000``.

.. code-block:: console

    $ muffin your.module run --host 0.0.0.0 --port 8000

``LOG_CONFIG`` from the application configuration is passed to uvicorn, so
logging behaves the same under the CLI and under a standalone server.

shell
~~~~~

Start an interactive shell with the application in scope.

.. code-block:: console

    $ muffin your.module shell
    $ muffin your.module shell --no-ipython

The shell is IPython when it is installed, and the standard ``code.interact``
otherwise; ``--no-ipython`` forces the latter. The context comes from
``MANAGE_SHELL``: by default it holds ``app``, ``run``, ``lifespan`` and one
entry per registered plugin.
Change the context with a mapping or a callable:

.. code-block:: python

    app.manage.shell({"app": app, "db": app.plugins["db"]})

Custom commands
---------------

Register a command with ``app.manage``. The function name becomes the command
name, with underscores turned into dashes:

.. code-block:: python

    @app.manage
    async def hello(name, upper=False):
        """Say hello to someone.

        :param name: Your name
        :param upper: Use uppercase
        """
        greetings = f"Hello {name}!"
        if upper:
            greetings = greetings.upper()
        print(greetings)

.. code-block:: console

    $ muffin example hello mike --upper
    HELLO MIKE!
    $ muffin example hello --help
    Say hello to someone.

    positional arguments:
      name        Your name

    options:
      -h, --help  show this help message and exit
      --upper     Use uppercase

Arguments are generated from the signature and the docstring:

- parameters without a default become positional arguments
- ``bool`` defaults become ``--flag`` (default ``False``) or ``--no-flag``
  (default ``True``)
- other defaults become optional arguments with the default shown in the help
- list defaults accumulate: pass the option once per value
- annotations are used as the argument type; ``*args`` collects the rest

The first line of the docstring becomes the command description; ``:param
name:`` lines become the argument help. Pass ``name=`` to set the command name
explicitly:

.. code-block:: python

    @app.manage(name="say-hello")
    async def hello(name):
        ...

Async commands run inside the application's async library. Pass
``lifespan=True`` to run one inside the application lifespan, which is what you
want when the command needs plugin connections:

.. code-block:: python

    @app.manage(lifespan=True)
    async def cleanup():
        """Drop expired sessions."""
        await app.plugins["db"].cleanup()

Uncaught exceptions from a command are logged and turn into a non-zero exit
code, so commands are safe to use in scripts.
