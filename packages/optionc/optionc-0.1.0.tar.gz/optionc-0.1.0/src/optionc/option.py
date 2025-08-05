from typing import TypeVar, Generic, Callable, Union, Any, Optional, Iterator

T = TypeVar('T')
U = TypeVar('U')


class Option(Generic[T]):
    
    def __new__(cls, value: Optional[T] = None) -> 'Option[T]':
        """Scala-like constructor: Option(x) creates Some(x) or Nil()"""
        if cls is not Option:
            # Direct subclass instantiation (Some, Nil)
            return super().__new__(cls)
        
        # Option(x) factory behavior
        if value is None:
            from .nil import Nil
            return Nil()
        else:
            from .some import Some
            return Some(value)
    
    def is_defined(self) -> bool:
        """Returns True if this Option has a value, False otherwise."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def is_empty(self) -> bool:
        """Returns True if this Option is empty, False otherwise."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def get(self) -> T:
        """Get the value of this Option. Raises exception if empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Get the value or return default if empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def or_else(self, alternative: Union['Option[T]', Callable[[], 'Option[T]']]) -> 'Option[T]':
        """Return this Option if defined, otherwise return alternative."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def map(self, func: Callable[[T], U]) -> 'Option[U]':
        """Transform the value if present, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def flat_map(self, func: Callable[[T], 'Option[U]']) -> 'Option[U]':
        """Transform the value to Option if present, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """Keep value if predicate is true, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def filter_not(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """Keep value if predicate is false, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        """Apply func to value if present, otherwise return if_empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def for_each(self, func: Callable[[T], Any]) -> None:
        """Apply func to value if present."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def exists(self, predicate: Callable[[T], bool]) -> bool:
        """True if value exists and satisfies predicate."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def for_all(self, predicate: Callable[[T], bool]) -> bool:
        """True if empty or value satisfies predicate."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def to_list(self) -> list[T]:
        """Convert to list - empty list if empty, single-item list if defined."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def to_optional(self) -> Optional[T]:
        """Convert to Optional - None if empty, value if defined."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    # Safe variants that catch exceptions and return Nil on failure
    def map_safe(self, func: Callable[[T], U]) -> 'Option[U]':
        """Transform the value if present, return Nil on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def flat_map_safe(self, func: Callable[[T], 'Option[U]']) -> 'Option[U]':
        """Transform the value to Option if present, return Nil on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def filter_safe(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """Keep value if predicate is true, return Nil on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def fold_safe(self, if_empty: U, func: Callable[[T], U]) -> U:
        """Apply func to value if present, return if_empty on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def for_each_safe(self, func: Callable[[T], Any]) -> None:
        """Apply func to value if present, ignore exceptions."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def exists_safe(self, predicate: Callable[[T], bool]) -> bool:
        """True if value exists and satisfies predicate, False on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def for_all_safe(self, predicate: Callable[[T], bool]) -> bool:
        """True if empty or value satisfies predicate, False on exception."""
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def __bool__(self) -> bool:
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def __repr__(self) -> str:
        raise NotImplementedError("Use Some or Nil, not Option directly")
    
    def __str__(self) -> str:
        raise NotImplementedError("Use Some or Nil, not Option directly")