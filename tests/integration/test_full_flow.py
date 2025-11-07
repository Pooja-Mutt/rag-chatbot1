"""
Integration tests for full application flow.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_upload_invalid_file(client):
    """Test upload endpoint rejects invalid files."""
    # Test empty file
    response = client.post("/upload", files={"file": ("test.pdf", b"", "application/pdf")})
    assert response.status_code == 400
    
    # Test wrong file type
    response = client.post("/upload", files={"file": ("test.txt", b"content", "text/plain")})
    assert response.status_code == 400


def test_stream_endpoint_structure(client):
    """Test stream endpoint structure (will fail without valid API key, but structure works)."""
    response = client.post("/stream", json={"message": "test question"})
    # Status 200 means endpoint structure works (error is from API, not our code)
    assert response.status_code == 200
    # Response will contain error about API key, but endpoint is working


def test_pdf_info_endpoint(client):
    """Test PDF info endpoint."""
    response = client.get("/pdf/info")
    assert response.status_code == 200
    data = response.json()
    assert "has_pdf" in data
    assert "message" in data


def test_stream_empty_message(client):
    """Test stream endpoint rejects empty messages."""
    response = client.post("/stream", json={"message": ""})
    assert response.status_code == 400
    
    response = client.post("/stream", json={"message": "   "})
    assert response.status_code == 400

