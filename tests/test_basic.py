"""
Basic test suite to verify testing infrastructure is working.
These tests don't test actual application functionality.
"""

import pytest


def test_pytest_is_working():
    """Test that pytest is working correctly."""
    assert True


def test_basic_math():
    """Test basic mathematical operations."""
    assert 2 + 2 == 4
    assert 3 * 3 == 9


def test_string_operations():
    """Test basic string operations."""
    assert "hello" + " world" == "hello world"
    assert len("test") == 4


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert sum(test_list) == 6


def test_dictionary_operations():
    """Test basic dictionary operations."""
    test_dict = {"a": 1, "b": 2}
    assert test_dict["a"] == 1
    assert "b" in test_dict


if __name__ == "__main__":
    pytest.main([__file__]) 