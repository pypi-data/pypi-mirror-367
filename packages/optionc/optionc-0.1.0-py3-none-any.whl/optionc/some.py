from typing import Callable, Union, Any, Optional, Iterator
from .option import Option, T, U


class Some(Option[T]):
    
    def __init__(self, value: T) -> None:
        if value is None:
            raise ValueError("Cannot create Some with None value")
        self._value = value
    
    def is_defined(self) -> bool:
        return True
    
    def is_empty(self) -> bool:
        return False
    
    def get(self) -> T:
        return self._value
    
    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        return self._value
    
    def or_else(self, alternative: Union[Option[T], Callable[[], Option[T]]]) -> Option[T]:
        return self
    
    def map(self, func: Callable[[T], U]) -> Option[U]:
        result = func(self._value)
        from .option import Option
        return Option(result)
    
    def flat_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        return func(self._value)
    
    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        if predicate(self._value):
            return self
        else:
            from .option import Option
            return Option(None)
    
    def filter_not(self, predicate: Callable[[T], bool]) -> Option[T]:
        if not predicate(self._value):
            return self
        else:
            from .option import Option
            return Option(None)
    
    # Safe variants that catch exceptions
    def map_safe(self, func: Callable[[T], U]) -> Option[U]:
        try:
            result = func(self._value)
            from .option import Option
            return Option(result)
        except Exception:
            from .option import Option
            return Option(None)
    
    def flat_map_safe(self, func: Callable[[T], Option[U]]) -> Option[U]:
        try:
            return func(self._value)
        except Exception:
            from .option import Option
            return Option(None)
    
    def filter_safe(self, predicate: Callable[[T], bool]) -> Option[T]:
        try:
            if predicate(self._value):
                return self
            else:
                from .option import Option
                return Option(None)
        except Exception:
            from .option import Option
            return Option(None)
    
    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        return func(self._value)
    
    def for_each(self, func: Callable[[T], Any]) -> None:
        func(self._value)
    
    def exists(self, predicate: Callable[[T], bool]) -> bool:
        return predicate(self._value)
    
    def for_all(self, predicate: Callable[[T], bool]) -> bool:
        return predicate(self._value)
    
    # Safe variants that catch exceptions
    def fold_safe(self, if_empty: U, func: Callable[[T], U]) -> U:
        try:
            return func(self._value)
        except Exception:
            return if_empty
    
    def for_each_safe(self, func: Callable[[T], Any]) -> None:
        try:
            func(self._value)
        except Exception:
            pass
    
    def exists_safe(self, predicate: Callable[[T], bool]) -> bool:
        try:
            return predicate(self._value)
        except Exception:
            return False
    
    def for_all_safe(self, predicate: Callable[[T], bool]) -> bool:
        try:
            return predicate(self._value)
        except Exception:
            return False
    
    def to_list(self) -> list[T]:
        return [self._value]
    
    def to_optional(self) -> Optional[T]:
        return self._value
    
    def __bool__(self) -> bool:
        return True
    
    def __iter__(self) -> Iterator[T]:
        yield self._value
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Some):
            return self._value == other._value
        # Some is never equal to Nil or other types
        return False
    
    def __repr__(self) -> str:
        return f"Some({self._value!r})"
    
    def __str__(self) -> str:
        return self.__repr__()