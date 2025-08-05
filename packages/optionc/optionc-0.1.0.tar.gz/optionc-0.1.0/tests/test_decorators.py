"""
Tests for option decorators.
"""
import pytest
from optionc import Option, Some, Nil, option, option_safe


class TestOptionDecorator:
    """Test @option decorator."""
    
    def test_option_with_non_none_return(self):
        """@option should wrap non-None returns in Some."""
        @option
        def get_value() -> str:
            return "hello"
        
        result = get_value()
        assert isinstance(result, Some)
        assert result.get() == "hello"
    
    def test_option_with_none_return(self):
        """@option should wrap None returns in Nil."""
        @option
        def get_none() -> str:
            return None
        
        result = get_none()
        assert isinstance(result, Nil)
    
    def test_option_with_parameters(self):
        """@option should work with parameterized functions."""
        @option
        def add(a: int, b: int) -> int:
            return a + b
        
        result = add(2, 3)
        assert isinstance(result, Some)
        assert result.get() == 5
    
    def test_option_exception_propagates(self):
        """@option should let exceptions propagate normally."""
        @option
        def raises_error() -> str:
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            raises_error()
    
    def test_option_preserves_function_metadata(self):
        """@option should preserve original function metadata."""
        @option
        def documented_func() -> str:
            """This function has documentation."""
            return "result"
        
        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This function has documentation."
    
    def test_option_with_various_types(self):
        """@option should work with different return types."""
        @option
        def get_int() -> int:
            return 42
        
        @option
        def get_list() -> list:
            return [1, 2, 3]
        
        @option
        def get_dict() -> dict:
            return {"key": "value"}
        
        assert get_int().get() == 42
        assert get_list().get() == [1, 2, 3]
        assert get_dict().get() == {"key": "value"}
    
    def test_option_with_empty_collections(self):
        """@option should wrap empty collections as Some (not Nil)."""
        @option
        def get_empty_list() -> list:
            return []
        
        @option
        def get_empty_dict() -> dict:
            return {}
        
        @option
        def get_empty_string() -> str:
            return ""
        
        assert isinstance(get_empty_list(), Some)
        assert isinstance(get_empty_dict(), Some)
        assert isinstance(get_empty_string(), Some)


class TestOptionSafeDecorator:
    """Test @option_safe decorator."""
    
    def test_option_safe_with_non_none_return(self):
        """@option_safe should wrap non-None returns in Some."""
        @option_safe
        def get_value() -> str:
            return "hello"
        
        result = get_value()
        assert isinstance(result, Some)
        assert result.get() == "hello"
    
    def test_option_safe_with_none_return(self):
        """@option_safe should wrap None returns in Nil."""
        @option_safe
        def get_none() -> str:
            return None
        
        result = get_none()
        assert isinstance(result, Nil)
    
    def test_option_safe_catches_exceptions(self):
        """@option_safe should catch exceptions and return Nil."""
        @option_safe
        def raises_error() -> str:
            raise ValueError("test error")
        
        result = raises_error()
        assert isinstance(result, Nil)
    
    def test_option_safe_with_different_exceptions(self):
        """@option_safe should catch various exception types."""
        @option_safe
        def zero_division() -> float:
            return 1 / 0
        
        @option_safe
        def type_error() -> int:
            return int("not a number")
        
        @option_safe
        def key_error() -> str:
            return {}["missing_key"]
        
        assert isinstance(zero_division(), Nil)
        assert isinstance(type_error(), Nil)
        assert isinstance(key_error(), Nil)
    
    def test_option_safe_preserves_function_metadata(self):
        """@option_safe should preserve original function metadata."""
        @option_safe
        def documented_func() -> str:
            """This function has documentation."""
            return "result"
        
        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This function has documentation."
    
    def test_option_safe_with_parameters(self):
        """@option_safe should work with parameterized functions."""
        @option_safe
        def safe_divide(a: int, b: int) -> float:
            return a / b
        
        # Successful division
        result1 = safe_divide(10, 2)
        assert isinstance(result1, Some)
        assert result1.get() == 5.0
        
        # Division by zero
        result2 = safe_divide(10, 0)
        assert isinstance(result2, Nil)
    
    def test_option_safe_with_complex_logic(self):
        """@option_safe should handle complex functions safely."""
        @option_safe
        def complex_operation(data: dict) -> str:
            # Multiple potential failure points
            user = data["user"]
            profile = user["profile"] 
            email = profile["email"]
            domain = email.split("@")[1]
            return domain.upper()
        
        # Successful case
        valid_data = {
            "user": {
                "profile": {
                    "email": "alice@example.com"
                }
            }
        }
        result1 = complex_operation(valid_data)
        assert isinstance(result1, Some)
        assert result1.get() == "EXAMPLE.COM"
        
        # Various failure cases
        assert isinstance(complex_operation({}), Nil)
        assert isinstance(complex_operation({"user": {}}), Nil)
        assert isinstance(complex_operation({"user": {"profile": {}}}), Nil)
        assert isinstance(complex_operation({"user": {"profile": {"email": "invalid"}}}), Nil)


class TestDecoratorComparison:
    """Test comparing @option vs @option_safe behavior."""
    
    def test_exception_handling_difference(self):
        """Demonstrate the key difference in exception handling."""
        @option
        def normal_parse(s: str) -> int:
            return int(s)
        
        @option_safe
        def safe_parse(s: str) -> int:
            return int(s)
        
        # Both succeed with valid input
        assert normal_parse("42").get() == 42
        assert safe_parse("42").get() == 42
        
        # Different behavior with invalid input
        with pytest.raises(ValueError):
            normal_parse("not a number")
        
        assert isinstance(safe_parse("not a number"), Nil)
    
    def test_none_handling_identical(self):
        """Both decorators handle None returns identically."""
        @option
        def normal_none() -> str:
            return None
        
        @option_safe  
        def safe_none() -> str:
            return None
        
        assert isinstance(normal_none(), Nil)
        assert isinstance(safe_none(), Nil)


class TestDecoratorIntegration:
    """Test decorators working with Option methods."""
    
    def test_decorated_function_chaining(self):
        """Test chaining methods on decorated function results."""
        @option_safe
        def parse_email(s: str) -> str:
            if "@" not in s:
                raise ValueError("Invalid email")
            return s.lower()
        
        @option_safe
        def extract_domain(email: str) -> str:
            return email.split("@")[1]
        
        # Chain operations
        result = (parse_email("ALICE@EXAMPLE.COM")
                 .flat_map(lambda email: extract_domain(email))
                 .map(lambda domain: domain.upper())
                 .filter(lambda domain: len(domain) > 3))
        
        assert isinstance(result, Some)
        assert result.get() == "EXAMPLE.COM"
        
        # Test failure case
        result2 = (parse_email("invalid-email")
                  .flat_map(lambda email: extract_domain(email)))
        assert isinstance(result2, Nil)
    
    def test_decorated_functions_with_utilities(self):
        """Test decorated functions working with utility functions."""
        from optionc import from_dict_get
        
        @option_safe
        def process_user_age(age_str: str) -> int:
            age = int(age_str)
            if age < 0 or age > 150:
                raise ValueError("Invalid age")
            return age
        
        user_data = {"age": "25", "name": "Alice"}
        
        result = (from_dict_get(user_data, "age")
                 .flat_map(lambda age_str: process_user_age(age_str))
                 .map(lambda age: f"Age: {age}"))
        
        assert isinstance(result, Some)
        assert result.get() == "Age: 25"
        
        # Test with invalid age
        invalid_data = {"age": "invalid", "name": "Bob"}
        result2 = (from_dict_get(invalid_data, "age")
                  .flat_map(lambda age_str: process_user_age(age_str)))
        assert isinstance(result2, Nil)


class TestDecoratorEdgeCases:
    """Test edge cases for decorators."""
    
    def test_decorated_methods(self):
        """Test decorators on class methods."""
        class Calculator:
            @option_safe
            def divide(self, a: int, b: int) -> float:
                return a / b
            
            @option
            def multiply(self, a: int, b: int) -> int:
                return a * b
        
        calc = Calculator()
        
        # Safe method
        assert calc.divide(10, 2).get() == 5.0
        assert isinstance(calc.divide(10, 0), Nil)
        
        # Normal method
        assert calc.multiply(3, 4).get() == 12
    
    def test_decorated_functions_with_default_args(self):
        """Test decorators with functions that have default arguments."""
        @option_safe
        def greet(name: str, greeting: str = "Hello") -> str:
            if not name.strip():
                raise ValueError("Name cannot be empty")
            return f"{greeting}, {name}!"
        
        assert greet("Alice").get() == "Hello, Alice!"
        assert greet("Bob", "Hi").get() == "Hi, Bob!"
        assert isinstance(greet(""), Nil)
    
    def test_decorated_generator_functions(self):
        """Test decorators with generator functions."""
        @option
        def get_range(n: int) -> range:
            return range(n)
        
        result = get_range(5)
        assert isinstance(result, Some)
        assert list(result.get()) == [0, 1, 2, 3, 4]