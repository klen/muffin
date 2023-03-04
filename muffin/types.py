from collections.abc import Callable
from typing import Any, Mapping, TypeVar

TVShellCtx = TypeVar("TVShellCtx", bound=Callable[[], Mapping[str, Any]])
