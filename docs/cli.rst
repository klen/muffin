CLI integration
===============

Run in your shell:

.. code-block :: console

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

optional arguments:
  -h, --help    Show this help message and exit
  --no-ipython  Disable use ipython as shell

run
~~~
  
Usage: 

.. code-block:: console

  $ muffin run [-h] [--bind SOCKET] [--daemon] [--pid PID] [--no-reload]
             [--timeout TIMEOUT] [--name NAME]
             [--worker-class WORKER_CLASS] [--workers WORKERS]
             [--log-file LOG_FILE] [--access-logfile ACCESS_LOGFILE]

Run the application.

optional arguments:
  -h, --help                  show this help message and exit
  --bind SOCKET               The socket to bind ['127.0.0.1:5000']
  --daemon                    Enable daemonize the program
  --pid PID                   A filename to use for the PID file [None]
  --no-reload                 Disable restart workers when code changes
  --timeout SEC               Workers silent for more than this many seconds 
                              are killed and restarted [30]
  --name NAME                 A base to use with setproctitle for process naming ['app']
  --worker-class CLASS        The type of workers to use ['muffin.worker.GunicornWorker']
  --workers NUM               The number of worker processes for handling requests [1]
  --log-file FILE             The error log file to write to [None]
  --access-logfile FILE       The access log file to write to ['-']


collect
~~~~~~~



Write a custom command
----------------------

.. code-block:: python

    @app.manage.command
    def hello(name, upper=False):
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
