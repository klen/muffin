from typing import Any, Mapping, TypeVar

from asgi_tools.types import *  # noqa

TVShellCtx = TypeVar("TVShellCtx", bound=Callable[[], Mapping[str, Any]])
