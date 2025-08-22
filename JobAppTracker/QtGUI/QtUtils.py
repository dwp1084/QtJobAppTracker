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


def shorten_string(original_string: str, length: int) -> str:
    """
    Helper function to shorten a string down to a certain number of characters,
    with an additional ellipsis at the end
    :param original_string: Source string
    :param length: Maximum string length, not including ellipsis
    :return: Shortened string. If the resulting string is shorter, it will have
        an ellipsis appended to the end
    """
    if len(original_string) > length:
        substr = original_string[:length].strip()
        substr += "..."

        return substr

    return original_string
