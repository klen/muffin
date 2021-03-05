Configuration
=============

Muffin gets configuration options from python files. You have to specify
default configuration module name in your app initialization:

.. code-block:: python

    # Application arguments are configuration modules, first available will be used
    app = muffin.Application('config.local', 'config.production')

This configuration module path could be overriden by ``MUFFIN_CONFIG``
environment variable: ::

  $ MUFFIN_CONFIG=settings.local uvicorn your_project:app

Also you can redefine config parameters while initializing your application:

Configuration will be available through :attr:`app.cfg` attribute.

.. code-block:: python

  app = muffin.Application(DEBUG=True, ANY_OPTION='value', ONE_MORE='value2')

  assert app.cfg.DEBUG is True
  assert app.cfg.ANY_OPTION  == 'value'
  assert app.cfg.ANY_OPTION  == 'value2'


Default Application Options
---------------------------

Base Muffin options and default values:

.. code-block:: python

        # Application name (used as prefix for env variables, for logging, for plugins)
        'NAME': 'muffin',

        # Configuration module
        'CONFIG': None,

        # Enable debug mode
        'DEBUG': False

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


Environment variables
---------------------

Muffin reads configuration values from the current environment's variables
using the form: ``{app.name}_{option_name}``. By default Muffin parses env
values as a JSON.

Consider the options file ``settings.py``:

.. code-block:: python

   DEBUG = True
   DB_PARAMS = {"pool": 10}
   TOKEN: str = None

.. code-block:: python

   os.environ['TOKEN'] = 'value'  # simple strings supported as well
   os.environ['DEBUG'] = 'false'  # json boolean value
   os.environ['DB_PARAMS'] = '{"pool": 50}' # json too

   app = Muffin('app', 'settings')

   assert app.cfg.DEBUG is False
   assert app.cfg.DB_PARAMS == {'pool': 50}
   assert app.cfg.TOKEN == 'value'

Configuration precedence
------------------------

The order in which configuration values are read is:

* From default config;
* From the given python modules;
* From environment variables;
* From the given paramenters when initializing the app;


Configuring logging
-------------------

You can define your logging configurations with
`Python dictConfig format <https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema>`_
and place in ``LOG_CONFIG`` option:

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
