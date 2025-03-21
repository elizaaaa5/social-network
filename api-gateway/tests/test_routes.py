import pytest
import requests_mock

def test_api_gateway_register_success(client):
    with requests_mock.Mocker() as m:
        m.post("http://user-service:8000/register", json={"id": "test-id"})
        response = client.post("/api/v1/register", json={
            "login": "testuser",
            "email": "test@example.com",
            "password": "validpass123"
        })
        assert response.status_code == 200
        assert response.json()["id"] == "test-id"

def test_api_gateway_password_validation(client):
    response = client.post("/api/v1/register", json={
        "login": "testuser",
        "email": "test@example.com",
        "password": "short"
    })
    assert response.status_code == 422
    assert "at least 8 characters" in response.text

def test_api_gateway_error_propagation(client):
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
    with requests_mock.Mocker() as m:
        mock_response = {"email": "new@example.com"}
        m.put("http://user-service:8000/me", json=mock_response)
        
        response = client.put("/api/v1/me",
            headers={"Authorization": "Bearer validtoken"},
            json={"email": "new@example.com"}
        )
        
        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"
