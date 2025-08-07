import pytest
from datetime import datetime
from evolvishub_notification_adapter import Category

def test_category_creation():
    category = Category("test_category", "Test description")
    assert category.name == "test_category"
    assert category.description == "Test description"
    assert category.id is None
    assert isinstance(category.created_at, datetime)

def test_category_validation():
    # Test empty name
    with pytest.raises(ValueError, match="Category name cannot be empty"):
        Category("", "Test description")
    
    # Test invalid characters
    with pytest.raises(ValueError, match="Category name can only contain alphanumeric characters and underscores"):
        Category("test-category", "Test description")
    
    # Test valid name with underscore
    category = Category("test_category_123", "Test description")
    assert category.name == "test_category_123"

def test_category_to_dict():
    category = Category("test_category", "Test description", id=1)
    category_dict = category.to_dict()
    assert category_dict["id"] == 1
    assert category_dict["name"] == "test_category"
    assert category_dict["description"] == "Test description"
    assert isinstance(category_dict["created_at"], datetime)

def test_category_string_representation():
    category = Category("test_category", "Test description")
    assert str(category) == "test_category (Test description)"
    
    category_no_desc = Category("test_category")
    assert str(category_no_desc) == "test_category (No description)" 