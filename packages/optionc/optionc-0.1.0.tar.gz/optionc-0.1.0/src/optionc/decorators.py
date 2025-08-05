"""
Decorators for automatic Option wrapping of function returns.
"""
from functools import wraps
from typing import Callable, TypeVar, Any
from .option import Option

T = TypeVar('T')


def option(func: Callable[..., T]) -> Callable[..., 'Option[T]']:
    """
    Decorator that wraps function return values in Option.
    
    - Returns Some(result) for non-None values
    - Returns Nil() for None values  
    - Exceptions propagate normally (not caught)
    
    Example:
        @option
        def find_user(user_id: str) -> User:
            return database.get(user_id)  # Returns Option[User]
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> 'Option[T]':
        result = func(*args, **kwargs)
        return Option(result)
    
    return wrapper


def option_safe(func: Callable[..., T]) -> Callable[..., 'Option[T]']:
    """
    Decorator that safely wraps function return values in Option.
    
    - Returns Some(result) for non-None values
    - Returns Nil() for None values
    - Returns Nil() if function raises any exception
    
    Example:
        @option_safe
        def parse_int(s: str) -> int:
            return int(s)  # Returns Some(42) or Nil() on ValueError
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> 'Option[T]':
        try:
            result = func(*args, **kwargs)
            return Option(result)
        except Exception:
            from .nil import Nil
            return Nil()
    
    return wrapper