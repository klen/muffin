"""Implement Muffin Application."""

import typing as t
import logging

from asgi_tools import App as BaseApp
from modconfig import Config

from . import CONFIG_ENV_VARIABLE


class MuffinException(Exception):

    """Base class for Muffin Errors."""

    pass


class Application(BaseApp):

    """The Muffin Application."""

    # Default configuration values
    defaults: t.Dict = dict(

        # Path to configuration module
        CONFIG=None,

        # Enable debug mode (optional)
        DEBUG=False,

        # Router options
        TRIM_LAST_SLASH='/',

        # Static files options
        STATIC_URL_PREFIX='/static',
        STATIC_FOLDERS=[],

        # Logging options
        LOG_LEVEL='WARNING',
        LOG_FORMAT='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        LOG_DATE_FORMAT='[%Y-%m-%d %H:%M:%S]',
        LOG_CONFIG=None,

    )

    def __init__(self, name: str, *configs: str, **options):
        """Initialize the application."""
        from .plugin import BasePlugin

        self.name = name
        self.plugins: t.Dict[str, BasePlugin] = dict()

        # Setup the configuration
        self.cfg = Config(prefix="%s_" % name.upper(), **self.defaults)
        options['CONFIG'] = self.cfg.update_from_modules(*configs, 'env:%s' % CONFIG_ENV_VARIABLE)
        self.cfg.update(**options)
        self.cfg.update_from_env()

        # Setup CLI
        from .manage import Manager

        self.manage = Manager(self)

        # Setup logging
        LOG_CONFIG = self.cfg.get('LOG_CONFIG')
        if LOG_CONFIG and isinstance(LOG_CONFIG, dict) and LOG_CONFIG.get('version'):
            logging.config.dictConfig(LOG_CONFIG)  # type: ignore

        self.logger = logging.getLogger('muffin')
        self.logger.setLevel(self.cfg.LOG_LEVEL)
        self.logger.propagate = False
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                self.cfg.LOG_FORMAT, self.cfg.LOG_DATE_FORMAT))
            self.logger.addHandler(ch)

        super(Application, self).__init__(
            debug=self.cfg.DEBUG,
            logger=self.logger,
            trim_last_slash=self.cfg.TRIM_LAST_SLASH,
            static_folders=self.cfg.STATIC_FOLDERS,
            static_url_prefix=self.cfg.STATIC_URL_PREFIX,
        )

    def __repr__(self) -> str:
        """Human readable representation."""
        return "<muffin.Application: %s>" % self.name
