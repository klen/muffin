"""Muffin is a web framework to build ASGI applications."""

# Package information
# ===================

__version__ = "0.87.1"
__project__ = "muffin"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

from asgi_tools import ASGINotFound  # noqa
from asgi_tools import (ASGIConnectionClosed, ASGIError, ASGIMethodNotAllowed, Request, Response,
                        ResponseError, ResponseFile, ResponseHTML, ResponseJSON, ResponseRedirect,
                        ResponseSSE, ResponseStream, ResponseText, ResponseWebSocket)
from asgi_tools.tests import ASGITestClient as TestClient  # noqa


class MuffinException(ASGIError):

    """Base class for Muffin Errors."""

    pass


CONFIG_ENV_VARIABLE = "MUFFIN_CONFIG"


from .app import Application  # noqa
from .handler import Handler  # noqa

__all__ = (
    "ASGIConnectionClosed",
    "ASGIError",
    "ASGIMethodNotAllowed",
    "ASGINotFound",
    "Application",
    "Handler",
    "Request",
    "Response",
    "ResponseError",
    "ResponseFile",
    "ResponseHTML",
    "ResponseJSON",
    "ResponseRedirect",
    "ResponseSSE",
    "ResponseStream",
    "ResponseText",
    "ResponseWebSocket",
    "TestClient",
)
