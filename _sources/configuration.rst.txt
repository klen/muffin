Configuration
=============

Muffin uses flexible hierarchical configuration via Python modules, environment variables, and runtime parameters.

Basic usage
-----------

Provide configuration modules during application initialization:

.. code-block:: python

    # Pass configuration module names; the first existing will be used
    app = muffin.Application('config.local', 'config.production')

You can override the configuration module using the ``MUFFIN_CONFIG`` environment variable:

.. code-block:: console

  $ MUFFIN_CONFIG=settings.local uvicorn your_project:app

Additionally, you can override individual configuration options directly:

.. code-block:: python

  app = muffin.Application(DEBUG=True, ANY_OPTION='value', ONE_MORE='value2')

  assert app.cfg.DEBUG is True
  assert app.cfg.ANY_OPTION == 'value'
  assert app.cfg.ONE_MORE == 'value2'

The configuration is accessible via :attr:`app.cfg`.

Default Application Options
---------------------------

Here are the built-in options and their default values:

.. code-block:: python

    {
        # Application name (used for env prefixes, logging, plugin configs)
        'NAME': 'muffin',

        # Configuration module
        'CONFIG': None,

        # Enable debug mode
        'DEBUG': False,

        # Routing options
        'TRIM_LAST_SLASH': True,

        # Static files options
        'STATIC_URL_PREFIX': '/static',
        'STATIC_FOLDERS': [],

        # Logging options
        'LOG_LEVEL': 'WARNING',
        'LOG_FORMAT': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        'LOG_DATE_FORMAT': '[%Y-%m-%d %H:%M:%S]',
        'LOG_CONFIG': None,

        # Muffin shell context
        'MANAGE_SHELL': lambda: {'app': app, 'run': aio_run, **app.plugins},
    }

Environment variables
---------------------

Muffin reads environment variables in the form {APP_NAME}_{OPTION_NAME}. By default, values are parsed as JSON.

Example settings.py:

.. code-block:: python

  DEBUG = True
  DB_PARAMS = {'pool': 10}
  TOKEN: str = None

Override values with environment variables:

.. code-block:: python

   os.environ['APP_TOKEN'] = 'value'  # simple strings supported as well
   os.environ['APP_DEBUG'] = 'false'  # json boolean value
   os.environ['APP_DB_PARAMS'] = '{"pool": 50}' # json too

   app = Muffin('app', 'settings')

   assert app.cfg.DEBUG is False
   assert app.cfg.DB_PARAMS == {'pool': 50}
   assert app.cfg.TOKEN == 'value'

Configuration precedence
------------------------

The order in which configuration values are read is:

  1.	Defaults
	2.	Python config modules
	3.	Environment variables
	4.	Keyword arguments passed to Application

Logging configuration
---------------------

You can define logging settings using
`Python's dictConfig format <https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema>`_
format in the ``LOG_CONFIG`` option:

.. code-block:: python

    LOG_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
            },
        },
        'handlers': {
            'logfile': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'my_log.log',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 10
            },
        },
        'loggers': {
            '': {
                'handlers': ['logfile'],
                'level': 'ERROR'
            },
            'project': {
                'level': 'INFO',
                'propagate': True,
            },
        }
    }
