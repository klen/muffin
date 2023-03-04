"""Muffin is a web framework to build ASGI applications."""
from __future__ import annotations

from asgi_tools import (
    ASGIConnectionClosedError,
    ASGIError,
    ASGIInvalidMethodError,
    ASGINotFoundError,
    Request,
    Response,
    ResponseError,
    ResponseFile,
    ResponseHTML,
    ResponseJSON,
    ResponseRedirect,
    ResponseSSE,
    ResponseStream,
    ResponseText,
    ResponseWebSocket,
)
from asgi_tools.tests import ASGITestClient as TestClient

from .app import Application
from .errors import MuffinError
from .handler import Handler

__all__ = (
    "ASGIConnectionClosedError",
    "ASGIError",
    "ASGIInvalidMethodError",
    "ASGINotFoundError",
    "Application",
    "Handler",
    "MuffinError",
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
