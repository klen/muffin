Configuration
-------------

Muffin gets configuration options from python files. You have to specify
default configuration module name in your app initialization:

.. code-block:: python

  app = muffin.Application('myapp', CONFIG='config.debug')

This name could be overriden by ``MUFFIN_CONFIG`` environment variable: ::

  $ MUFFIN_CONFIG=settings_local muffin example run

Which in its turn could be overriden by ``--config`` param of ``muffin`` command: ::

  $ muffin --config=config.debug example run

Also you can define default config parameter values while initializing your application:

.. code-block:: python

  app = muffin.Application('myapp', DEBUG=True, ANY_OPTION='Here', ONE_MORE='Yes')

Base application options
^^^^^^^^^^^^^^^^^^^^^^^^

Base Muffin options and default values:

.. code-block:: python

        # Configuration module
        'CONFIG': 'config'

        # Enable debug mode
        'DEBUG': False

        # Logging options
        'ACCESS_LOG': '-',  # File path to access log, - to stderr
        'ACCESS_LOG_FORMAT': '%a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i"',

        'LOG_LEVEL': 'WARNING'
        'LOG_FORMAT': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s'
        'LOG_DATE_FORMAT': '[%Y-%m-%d %H:%M:%S %z]'

        # List of enabled plugins
        'PLUGINS': []

        # Setup static files in development
        'STATIC_PREFIX': '/static'
        'STATIC_FOLDERS': ['static']


Configuring logging
^^^^^^^^^^^^^^^^^^^
You can define your logging configurations with `Python dictConfig format  <https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema>`_ and place in ``LOGGING`` conf:

.. code-block:: python

    LOGGING = {
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

To use just get logger with ``logging.getLogger()``:

.. code-block:: python

    import logging
    logger = logging.getLogger('project')
