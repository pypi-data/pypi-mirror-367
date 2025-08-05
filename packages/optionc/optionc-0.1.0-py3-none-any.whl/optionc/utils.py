from typing import Optional, Callable, Any, TypeVar
from .option import Option as OptionType

T = TypeVar('T')


def from_callable(func: Callable[[], T]) -> OptionType[T]:
    """Create an Option by calling a function. Exceptions result in Nil."""
    try:
        result = func()
        from .option import Option
        return Option(result)
    except Exception:
        from .nil import Nil
        return Nil()


def from_dict_get(dictionary: dict, key: Any, default: Optional[T] = None) -> OptionType[T]:
    """Create an Option from dict.get()."""
    value = dictionary.get(key, default)
    from .option import Option
    return Option(value)


def from_getattr(obj: Any, attr: str, default: Optional[T] = None) -> OptionType[T]:
    """Create an Option from getattr()."""
    try:
        value = getattr(obj, attr, default)
        from .option import Option
        return Option(value)
    except Exception:
        from .nil import Nil
        return Nil()