from app.main import app
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def client():
    return TestClient(app)
