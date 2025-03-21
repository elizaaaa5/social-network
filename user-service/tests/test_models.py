import pytest
from app.main import UserCreate, UserUpdate
from datetime import date

def test_user_create_valid():
    valid_user = UserCreate(
        login="testuser",
        email="test@example.com",
        password="validpass123",
        first_name="Test"
    )
    assert valid_user.password == "validpass123"

def test_user_create_invalid_password():
    with pytest.raises(ValueError) as exc:
        UserCreate(
            login="testuser",
            email="test@example.com",
            password="short"
        )
    assert "at least 8 characters" in str(exc.value)

def test_user_update_password():
    update = UserUpdate(password="newpassword123")
    assert update.password == "newpassword123"
