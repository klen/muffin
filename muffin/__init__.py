"""Muffin is a web framework based on aiohttp."""

# Package information
# ===================

__version__ = "0.7.1"
__project__ = "muffin"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

from aiohttp.web import *

CONFIGURATION_ENVIRON_VARIABLE = 'MUFFIN_CONFIG'

from .app import Application, Handler
from .utils import to_coroutine, MuffinException, local, import_submodules

#  pylama:ignore=E402,W0611,W0401
