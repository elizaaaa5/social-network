import pytest
from fastapi.testclient import TestClient
import json
from app.models import UserDB

def test_register_user_success(client):
    """Test successful user registration"""
    response = client.post("/register", json={
        "login": "newuser",
        "email": "new@example.com",
        "password": "strongpassword123",
        "first_name": "New"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["login"] == "newuser"
    assert data["email"] == "new@example.com"
    assert data["first_name"] == "New"

def test_register_duplicate_user(client):
    """Test duplicate user registration fails"""
    # First registration
    client.post("/register", json={
        "login": "duplicate",
        "email": "dup@example.com",
        "password": "password123"
    })
    
    # Try duplicate login
    response = client.post("/register", json={
        "login": "duplicate",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already registered" in response.text

def test_login_success(client):
    """Test successful login"""
    # Register first
    client.post("/register", json={
        "login": "testlogin",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Successful login
    response = client.post("/token", data={
        "username": "testlogin",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/token", data={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Incorrect username or password" in response.text

def test_protected_route_unauthorized(client):
    """Test accessing protected route without token"""
    response = client.get("/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.text

def test_update_user_profile(client):
    """Test updating user profile"""
    # Register and login
    client.post("/register", json={
        "login": "updateuser",
        "email": "update@example.com",
        "password": "updatepass123"
    })
    login = client.post("/token", data={
        "username": "updateuser",
        "password": "updatepass123"
    })
    token = login.json()["access_token"]
    
    # Update profile
    response = client.put("/me", 
        json={"email": "newemail@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["login"] == "updateuser"  # Original data preserved
