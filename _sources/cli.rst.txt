CLI integration
===============

Muffin provides a built-in CLI to manage your application.

Run in your shell:

.. code-block:: console

    $ muffin path.to.your.module --help
    $ muffin path.to.your.module:app_object_name --help

This will list all available commands for your application.

Built-in commands
-----------------

shell
~~~~~

Start an interactive shell with your application context.

Usage:

.. code-block:: console

    $ muffin your.module shell [--no-ipython]

Options:

- ``--no-ipython`` – Disable IPython, use standard Python shell

Example:

.. code-block:: console

    $ muffin example shell

    Interactive Muffin Shell
    ------------------------
    Python: 3.11.0

    Loaded globals: ['app', 'run', ...]

Write a custom command
-----------------------

Define your own commands using :meth:`app.manage.command`:

.. code-block:: python

    @app.manage.command
    async def hello(name, upper=False):
        """Say hello to someone.

        :param name: Your name
        :param upper: Use uppercase
        """
        greetings = f"Hello {name}!"
        if upper:
            greetings = greetings.upper()
        print(greetings)

Run your command:

.. code-block:: console

    $ muffin example hello mike --upper
    HELLO MIKE!

Show help for your command:

.. code-block:: console

    $ muffin example hello --help

    Say hello to someone.

    positional arguments:
      name        Your name

    optional arguments:
      -h, --help  Show this help message and exit
      --upper     Enable use uppercase
      --no-upper  Disable use uppercase
