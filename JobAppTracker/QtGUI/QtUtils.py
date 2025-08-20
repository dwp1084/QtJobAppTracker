from typing import Protocol, Callable, Any


class QtSignal(Protocol):
    """
    This class acts as a type hint fix for the "pyqtSignal has no attribute
    'emit'" warning that comes up, but doesn't have a straight-forward fix.

    It has no added function, it's meant to supress a warning for a non-issue.
    """
    def connect(self, slot: Callable[..., Any]) -> None: ...
    def disconnect(self, slot: Callable[..., Any]) -> None: ...
    def emit(self, *args: Any, **kwargs: Any) -> None: ...
