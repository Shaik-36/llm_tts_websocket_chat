"""Test WebSocket endpoint"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


# ================================================================
# TEST 1: Health status
# ================================================================


def test_health_endpoint(client):
    """Should return healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ================================================================
# TEST 2: Service info
# ================================================================


def test_root_endpoint(client):
    """Should return service info"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


# ================================================================
# TEST 3: WebSocket connection
# ================================================================


def test_websocket_connection(client):
    """Should accept WebSocket connection"""
    with client.websocket_connect("/ws") as websocket:
        # Connection should be established
        assert websocket is not None


# ================================================================
# TEST 4: WebSocket Invalid Message Format
# ================================================================


def test_websocket_invalid_message(client):
    """Should handle invalid message format"""
    with client.websocket_connect("/ws") as websocket:
        # Send invalid JSON
        websocket.send_json({"invalid_field": "value"})
        
        # Should receive error
        data = websocket.receive_json()
        assert data["type"] == "error"
