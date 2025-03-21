import pytest
from datetime import date
import uuid
from app.main import UserCreate, UserUpdate
from app.models import UserDB

def test_user_create_valid():
    """Test that a valid user can be created"""
    user = UserCreate(
        login="testuser",
        email="test@example.com",
        password="validpass123",
        first_name="Test"
    )
    assert user.login == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "validpass123"
    assert user.first_name == "Test"

def test_user_create_invalid_password():
    """Test that password validation works"""
    with pytest.raises(ValueError) as exc:
        UserCreate(
            login="testuser",
            email="test@example.com",
            password="short"  # Too short
        )
    assert "at least 8 characters" in str(exc.value)

def test_user_update_password():
    """Test that password can be updated"""
    update = UserUpdate(password="newpassword123")
    assert update.password == "newpassword123"
    
    # Test validation still works
    with pytest.raises(ValueError):
        UserUpdate(password="short")

def test_user_db_model():
    """Test UserDB model properties"""
    user_id = uuid.uuid4()
    user = UserDB(
        id=user_id,
        login="testdb",
        email="testdb@example.com",
        password_hash="hash$value",
        first_name="Test",
        last_name="User",
        birth_date=date(1990, 1, 1)
    )
    
    assert user.id == user_id
    assert user.login == "testdb"
    assert user.email == "testdb@example.com"
    assert user.password_hash == "hash$value"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.birth_date == date(1990, 1, 1)
