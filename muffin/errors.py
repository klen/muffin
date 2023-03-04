from __future__ import annotations

from typing import TYPE_CHECKING

from asgi_tools import ASGIError

if TYPE_CHECKING:
    from typing import Callable


class MuffinError(ASGIError):

    """Base class for Muffin Errors."""


class AsyncRequiredError(TypeError):

    """Raised when an async function is required."""

    def __init__(self, func: Callable):
        """Initialize the exception."""
        super().__init__(f"Function {func.__qualname__} has to be async")


class InvalidAppError(ImportError):

    """Raised when an application is not found."""

    def __init__(self, name: str):
        """Initialize the exception."""
        super().__init__(f"Application {name!r} not found")
