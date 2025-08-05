"""
Tests for utility functions.
"""
import pytest
from optionc import Option, Some, Nil, from_callable, from_dict_get, from_getattr


class TestFromCallable:
    """Test from_callable() utility function."""
    
    def test_from_callable_success(self):
        """from_callable() should return Some when function succeeds."""
        result = from_callable(lambda: "hello")
        assert isinstance(result, Some)
        assert result.get() == "hello"
    
    def test_from_callable_with_none_result(self):
        """from_callable() should return Nil when function returns None."""
        result = from_callable(lambda: None)
        assert isinstance(result, Nil)
    
    def test_from_callable_exception(self):
        """from_callable() should return Nil when function raises exception."""
        result = from_callable(lambda: 1 / 0)
        assert isinstance(result, Nil)
    
    def test_from_callable_with_arguments(self):
        """from_callable() with parameterized functions."""
        def computation():
            return 2 + 2
        
        result = from_callable(computation)
        assert isinstance(result, Some)
        assert result.get() == 4
    
    def test_from_callable_with_side_effects(self):
        """from_callable() should execute side effects even if result is None."""
        side_effect_tracker = []
        
        def side_effect_func():
            side_effect_tracker.append("executed")
            return None
        
        result = from_callable(side_effect_func)
        assert isinstance(result, Nil)
        assert side_effect_tracker == ["executed"]


class TestFromDictGet:
    """Test from_dict_get() utility function."""
    
    def test_from_dict_get_existing_key(self):
        """from_dict_get() should return Some for existing key."""
        data = {"name": "Alice", "age": 25}
        result = from_dict_get(data, "name")
        assert isinstance(result, Some)
        assert result.get() == "Alice"
    
    def test_from_dict_get_missing_key(self):
        """from_dict_get() should return Nil for missing key."""
        data = {"name": "Alice", "age": 25}
        result = from_dict_get(data, "email")
        assert isinstance(result, Nil)
    
    def test_from_dict_get_with_default(self):
        """from_dict_get() should use default value for missing key."""
        data = {"name": "Alice"}
        result = from_dict_get(data, "age", 0)
        assert isinstance(result, Some)
        assert result.get() == 0
    
    def test_from_dict_get_with_none_default(self):
        """from_dict_get() should return Nil when default is None."""
        data = {"name": "Alice"}
        result = from_dict_get(data, "age", None)
        assert isinstance(result, Nil)
    
    def test_from_dict_get_various_types(self):
        """from_dict_get() should work with different value types."""
        data = {
            "string": "hello",
            "int": 42,
            "list": [1, 2, 3],
            "none": None,
            "empty_string": "",
            "zero": 0,
            "false": False
        }
        
        assert from_dict_get(data, "string").get() == "hello"
        assert from_dict_get(data, "int").get() == 42
        assert from_dict_get(data, "list").get() == [1, 2, 3]
        assert from_dict_get(data, "none").is_empty()
        assert from_dict_get(data, "empty_string").get() == ""
        assert from_dict_get(data, "zero").get() == 0
        assert from_dict_get(data, "false").get() is False


class TestFromGetattr:
    """Test from_getattr() utility function."""
    
    def test_from_getattr_existing_attribute(self):
        """from_getattr() should return Some for existing attribute."""
        class TestObj:
            attr = "value"
        
        obj = TestObj()
        result = from_getattr(obj, "attr")
        assert isinstance(result, Some)
        assert result.get() == "value"
    
    def test_from_getattr_missing_attribute(self):
        """from_getattr() should return Nil for missing attribute."""
        class TestObj:
            pass
        
        obj = TestObj()
        result = from_getattr(obj, "missing")
        assert isinstance(result, Nil)
    
    def test_from_getattr_with_default(self):
        """from_getattr() should use default for missing attribute."""
        class TestObj:
            pass
        
        obj = TestObj()
        result = from_getattr(obj, "missing", "default")
        assert isinstance(result, Some)
        assert result.get() == "default"
    
    def test_from_getattr_with_none_default(self):
        """from_getattr() should return Nil when default is None."""
        class TestObj:
            pass
        
        obj = TestObj()
        result = from_getattr(obj, "missing", None)
        assert isinstance(result, Nil)
    
    def test_from_getattr_with_property(self):
        """from_getattr() should work with properties."""
        class TestObj:
            @property
            def computed(self):
                return "computed_value"
        
        obj = TestObj()
        result = from_getattr(obj, "computed")
        assert isinstance(result, Some)
        assert result.get() == "computed_value"
    
    def test_from_getattr_with_method(self):
        """from_getattr() should work with methods."""
        class TestObj:
            def method(self):
                return "method_result"
        
        obj = TestObj()
        result = from_getattr(obj, "method")
        assert isinstance(result, Some)
        # Should return the method object, not call it
        assert callable(result.get())
    
    def test_from_getattr_exception_handling(self):
        """from_getattr() should return Nil on exceptions."""
        class BadProperty:
            @property
            def error_prop(self):
                raise ValueError("Property error")
        
        obj = BadProperty()
        result = from_getattr(obj, "error_prop")
        assert isinstance(result, Nil)


class TestUtilityIntegration:
    """Test utility functions working together."""
    
    def test_chaining_utilities_with_methods(self):
        """Test chaining utility functions with Option methods."""
        data = {"user": {"profile": {"email": "alice@example.com"}}}
        
        result = (from_dict_get(data, "user")
                 .flat_map(lambda user: from_dict_get(user, "profile"))
                 .flat_map(lambda profile: from_dict_get(profile, "email"))
                 .filter(lambda email: "@" in email)
                 .map(lambda email: email.split("@")[1]))
        
        assert isinstance(result, Some)
        assert result.get() == "example.com"
    
    def test_safe_object_navigation(self):
        """Test safe object navigation using utilities."""
        class User:
            def __init__(self, name, profile=None):
                self.name = name
                self.profile = profile
        
        class Profile:
            def __init__(self, email=None):
                self.email = email
        
        # User with profile
        user1 = User("Alice", Profile("alice@example.com"))
        result1 = (from_getattr(user1, "profile")
                  .flat_map(lambda p: from_getattr(p, "email")))
        assert isinstance(result1, Some)
        assert result1.get() == "alice@example.com"
        
        # User without profile
        user2 = User("Bob")
        result2 = (from_getattr(user2, "profile")
                  .flat_map(lambda p: from_getattr(p, "email")))
        assert isinstance(result2, Nil)
        
        # User with profile but no email
        user3 = User("Charlie", Profile())
        result3 = (from_getattr(user3, "profile")
                  .flat_map(lambda p: from_getattr(p, "email")))
        assert isinstance(result3, Nil)
    
    def test_config_loading_pattern(self):
        """Test common configuration loading pattern."""
        import os
        
        def load_config():
            # Try multiple sources
            return (from_callable(lambda: os.environ.get("CONFIG_FILE"))
                   .or_else(lambda: Option("default_config.json"))
                   .flat_map(lambda path: from_callable(lambda: f"loaded from {path}")))
        
        config = load_config()
        assert isinstance(config, Some)
        assert "loaded from" in config.get()


class TestEdgeCases:
    """Test edge cases for utility functions."""
    
    def test_utilities_with_complex_types(self):
        """Test utilities with complex types."""
        complex_data = {
            "nested": {
                "list": [{"item": "value"}],
                "tuple": (1, 2, 3),
                "set": {1, 2, 3}
            }
        }
        
        result = (from_dict_get(complex_data, "nested")
                 .flat_map(lambda n: from_dict_get(n, "list"))
                 .filter(lambda lst: len(lst) > 0)
                 .map(lambda lst: lst[0])
                 .flat_map(lambda item: from_dict_get(item, "item")))
        
        assert isinstance(result, Some)
        assert result.get() == "value"
    
    def test_utilities_preserve_type_information(self):
        """Test that utilities preserve type information correctly."""
        # Test with different numeric types using Option constructor
        assert Option(42).get() == 42
        assert Option(3.14).get() == 3.14
        assert Option(complex(1, 2)).get() == complex(1, 2)
        
        # Test with boolean
        assert Option(True).get() is True
        assert Option(False).get() is False
