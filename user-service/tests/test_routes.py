import pytest
from app.main import UserDB

def test_register_user_success(client):
    response = client.post("/register", json={
        "login": "newuser",
        "email": "new@example.com",
        "password": "strongpassword123",
        "first_name": "New"
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_register_duplicate_user(client):
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
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post("/token", data={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Incorrect username or password" in response.text

def test_protected_route_unauthorized(client):
    response = client.get("/me")
    assert response.status_code == 401

def test_update_user_profile(client):
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
    assert response.json()["email"] == "newemail@example.com"
