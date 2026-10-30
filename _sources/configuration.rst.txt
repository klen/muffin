Configuration
=============

Configuration is read from four places. The later ones win:

1. Application defaults
2. Python configuration modules
3. Keyword arguments passed to ``Application()``
4. Environment variables

Basic usage
-----------

Pass module paths during initialization. The modules are tried in order and the
first one that exists is used:

.. code-block:: python

    import muffin

    app = muffin.Application("config.local", "config.production")

The module can be replaced with the ``MUFFIN_CONFIG`` environment variable,
which is what the CLI ``--config`` option sets:

.. code-block:: console

  $ MUFFIN_CONFIG=settings.local uvicorn your_project:app

Single values can be overridden in place:

.. code-block:: python

    app = muffin.Application(DEBUG=True, ANY_OPTION="value", ONE_MORE="value2")

    assert app.cfg.DEBUG is True
    assert app.cfg.ANY_OPTION == "value"
    assert app.cfg.ONE_MORE == "value2"

All of it is available as :attr:`app.cfg`.

Default application options
---------------------------

.. code-block:: python

    {
        # Application name: env prefix, logger, plugin configs
        "NAME": "muffin",

        # Configuration module that was actually loaded
        "CONFIG": None,

        # Debug mode
        "DEBUG": False,

        # Ignore a trailing slash when matching routes
        "TRIM_LAST_SLASH": True,

        # Compare routes against the Host header
        "USE_HOSTS": False,

        # Static files
        "STATIC_URL_PREFIX": "/static",
        "STATIC_FOLDERS": [],

        # Logging
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
        "LOG_DATE_FORMAT": "[%Y-%m-%d %H:%M:%S]",
        "LOG_CONFIG": None,
    }

``NAME`` matters more than it looks: it prefixes environment variables and
selects the plugin configuration keys, so a real project sets it early, usually
in the configuration module.

Environment variables
---------------------

Every option can be set as ``{NAME}_{OPTION}``. With the default name that means
``MUFFIN_*``:

.. code-block:: console

  $ MUFFIN_DEBUG=true MUFFIN_DB_PARAMS='{"pool": 50}' uvicorn app:app

Values are parsed as JSON when possible, which covers booleans, numbers, lists
and dicts. Plain strings are accepted as they are. A type annotation on the
option is respected by the parser.

Given ``settings.py``:

.. code-block:: python

  DEBUG = True
  DB_PARAMS = {"pool": 10}
  TOKEN: str = None

these variables

.. code-block:: python

   os.environ["MUFFIN_TOKEN"] = "value"
   os.environ["MUFFIN_DEBUG"] = "false"
   os.environ["MUFFIN_DB_PARAMS"] = '{"pool": 50}'

produce:

.. code-block:: python

   app = muffin.Application("settings")

   assert app.cfg.DEBUG is False
   assert app.cfg.DB_PARAMS == {"pool": 50}
   assert app.cfg.TOKEN == "value"

Plugin configuration
--------------------

A plugin reads options from the application config with the ``{PLUGIN_NAME}_``
prefix. Precedence, lowest to highest:

1. Plugin ``defaults``
2. Application config keys with the ``{PLUGIN_NAME}_`` prefix
3. Keyword arguments passed to ``Plugin(app, ...)``
4. Environment variables ``{APP_NAME}_{PLUGIN_NAME}_{OPTION}``

.. code-block:: python

   os.environ["MUFFIN_PLUGIN_OPTION"] = "33"

   class Plugin(BasePlugin):
       name = "plugin"
       defaults = {"option": 11}

   app = Application()
   plugin = Plugin(app)
   assert plugin.cfg.option == 33

A plugin is registered in ``app.plugins`` unless ``disabled`` is set in its
config. Disabled plugins are skipped with a warning in the log.

Logging
-------

``LOG_LEVEL``, ``LOG_FORMAT`` and ``LOG_DATE_FORMAT`` cover the usual case. For
anything else, put a full `dictConfig`_ mapping into ``LOG_CONFIG``:

.. code-block:: python

    LOG_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
        },
        "handlers": {
            "logfile": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "my_log.log",
                "maxBytes": 50 * 1024 * 1024,
                "backupCount": 10,
            },
        },
        "loggers": {
            "": {"handlers": ["logfile"], "level": "ERROR"},
            "project": {"level": "INFO", "propagate": True},
        },
    }

The same mapping is passed to uvicorn when the app is started with ``muffin
<module> run``.

.. _dictConfig: https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema
