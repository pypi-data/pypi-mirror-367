from typing import Optional, Callable, Union, Any, Iterator
from .option import Option, T, U


class NilType(Option[T]):
    
    _instance: Optional['NilType'] = None
    
    def __new__(cls) -> 'NilType':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def is_defined(self) -> bool:
        return False
    
    def is_empty(self) -> bool:
        return True
    
    def get(self) -> T:
        raise ValueError("Cannot get value from empty Option")
    
    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        if callable(default):
            try:
                return default()
            except Exception:
                raise ValueError("Default function failed and Option is empty")
        return default
    
    def or_else(self, alternative: Union[Option[T], Callable[[], Option[T]]]) -> Option[T]:
        if callable(alternative):
            try:
                return alternative()
            except Exception:
                return self
        return alternative
    
    def map(self, func: Callable[[T], U]) -> Option[U]:
        # Nil maps to Nil regardless of function
        return Nil()
    
    def flat_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        # Nil flat_maps to Nil regardless of function
        return Nil()
    
    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        # Nil filters to Nil regardless of predicate
        return self
    
    def filter_not(self, predicate: Callable[[T], bool]) -> Option[T]:
        # Nil filters to Nil regardless of predicate
        return self
    
    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        # Nil always returns the empty value
        return if_empty
    
    def for_each(self, func: Callable[[T], Any]) -> None:
        # Nil does nothing
        pass
    
    def exists(self, predicate: Callable[[T], bool]) -> bool:
        # Nil never satisfies any predicate
        return False
    
    def for_all(self, predicate: Callable[[T], bool]) -> bool:
        # Nil vacuously satisfies all predicates
        return True
    
    # Safe variants (same as regular for Nil since no function is called)
    def map_safe(self, func: Callable[[T], U]) -> Option[U]:
        return Nil()
    
    def flat_map_safe(self, func: Callable[[T], Option[U]]) -> Option[U]:
        return Nil()
    
    def filter_safe(self, predicate: Callable[[T], bool]) -> Option[T]:
        return self
    
    def fold_safe(self, if_empty: U, func: Callable[[T], U]) -> U:
        return if_empty
    
    def for_each_safe(self, func: Callable[[T], Any]) -> None:
        pass
    
    def exists_safe(self, predicate: Callable[[T], bool]) -> bool:
        return False
    
    def for_all_safe(self, predicate: Callable[[T], bool]) -> bool:
        return True
    
    def to_list(self) -> list[T]:
        # Nil converts to empty list
        return []
    
    def to_optional(self) -> Optional[T]:
        # Nil converts to None
        return None
    
    def __bool__(self) -> bool:
        return False
    
    def __iter__(self) -> Iterator[T]:
        # Nil yields nothing
        return iter([])
    
    def __eq__(self, other: object) -> bool:
        # Nil is equal to other Nil instances
        return isinstance(other, NilType)
    
    def __repr__(self) -> str:
        return "Nil()"
    
    def __str__(self) -> str:
        return self.__repr__()


# Create singleton instance
Nil = NilType