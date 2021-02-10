CLI integration
===============

Run in your shell:

.. code-block:: console

    $ muffin path.to.your.module --help
    $ muffin path.to.your.module:app_object_name --help
    
You'll see commands available for your application.

Built-in commands
-----------------

shell
~~~~~
  
Usage: 

.. code-block:: console

  $ muffin shell [-h] [--no-ipython]

Run the application shell.

Optional arguments:
  -h, --help    Show this help message and exit
  --no-ipython  Disable use ipython as shell


Write a custom command
----------------------

.. code-block:: python

    @app.manage.command
    async def hello(name, upper=False):
        """ Write command help text here.

        :param name:  Write your name
        :param upper: Use uppercase

        """
        greetings = 'Hello %s!' % name
        if upper:
            greetings = greetings.upper()
        print(greetings)

.. code-block:: console

    $ muffin example hello --help

        Write command help text here.

        positional arguments:
        name        Write your name

        optional arguments:
        -h, --help  show this help message and exit
        --upper     Enable use uppercase
        --no-upper  Disable use uppercase

    $ muffin example hello mike --upper

        HELLO MIKE!
