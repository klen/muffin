"""
    muffin description.

"""

# Package information
# ===================

__version__ = "0.0.4"
__project__ = "muffin"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

from asyncio import *           # noqa

from aiohttp.web import *       # noqa

from .app import Application    # noqa
