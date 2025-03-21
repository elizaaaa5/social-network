import pytest
import requests_mock
from fastapi.testclient import TestClient

def test_api_gateway_register_success(client):
    """Test successful user registration through API gateway"""
    with requests_mock.Mocker() as m:
        m.post("http://user-service:8000/register", json={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "login": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        })
        
        response = client.post("/api/v1/register", json={
            "login": "testuser",
            "email": "test@example.com",
            "password": "validpass123",
            "first_name": "Test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["login"] == "testuser"
        assert data["email"] == "test@example.com"

def test_api_gateway_password_validation(client):
    """Test password validation in API gateway"""
    response = client.post("/api/v1/register", json={
        "login": "testuser",
        "email": "test@example.com",
        "password": "short"  # Too short
    })
    
    assert response.status_code == 422
    assert "at least 8 characters" in response.text

def test_api_gateway_error_propagation(client):
    """Test error propagation from user service"""
    with requests_mock.Mocker() as m:
        m.post("http://user-service:8000/register", 
              status_code=400,
              json={"detail": "Username taken"})
        
        response = client.post("/api/v1/register", json={
            "login": "existing",
            "email": "existing@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
        assert "Username taken" in response.text

def test_api_gateway_update_profile(client):
    """Test profile update through API gateway"""
    with requests_mock.Mocker() as m:
        # Mock the validation token request
        m.get("http://user-service:8000/me", json={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "login": "testuser",
            "email": "old@example.com"
        })
        
        # Mock the update request
        m.put("http://user-service:8000/me", json={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "login": "testuser",
            "email": "new@example.com"
        })
        
        response = client.put("/api/v1/me",
            headers={"Authorization": "Bearer validtoken"},
            json={"email": "new@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
