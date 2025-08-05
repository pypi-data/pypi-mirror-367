"""
optionc - Scala-inspired Option type for Python

A functional programming library providing Some/Nil types for safe handling
of nullable values, inspired by Scala's Option type.

Example usage:
    from optionc import Option, Some, Nil
    
    # Create options (Scala-like)
    user = Option("john@example.com")  # Some("john@example.com")
    empty = Option(None)               # Nil()
    
    # Or create directly
    user = Some("john@example.com")
    empty = Nil()
    
    # Safe transformations
    result = user.map(str.upper).filter(lambda s: '@' in s)
    
    # Handle missing values
    email = result.get_or_else("no-email@example.com")
    
    # Utility functions for common patterns
    config_val = from_dict_get(config, "timeout", 30)
    attr_val = from_getattr(obj, "property", "default")
    computed = from_callable(lambda: expensive_computation())
"""

from .option import Option
from .some import Some
from .nil import Nil
from .utils import from_callable, from_dict_get, from_getattr
from .decorators import option, option_safe

__version__ = "0.1.0"
__author__ = "Carl You"
__email__ = ""

__all__ = [
    # Core types and constructor (Scala-like)
    "Option",  # Both type annotation and constructor: Option(x) 
    "Some",    # Direct construction: Some(x)
    "Nil",     # Direct construction: Nil()
    # Utility functions for common patterns
    "from_callable",  # from_callable(lambda: func())
    "from_dict_get",  # from_dict_get(dict, key, default)
    "from_getattr",   # from_getattr(obj, attr, default)
    # Decorators for automatic Option wrapping
    "option",         # @option - wrap returns, exceptions propagate
    "option_safe",    # @option_safe - wrap returns, catch exceptions
]