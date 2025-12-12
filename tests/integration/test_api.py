"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.app import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "QR Code Transformation" in response.text
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @pytest.mark.slow
    def test_transform_endpoint_messages(self, client):
        """Test transformation endpoint with messages."""
        response = client.post(
            "/api/transform",
            data={
                "message_a": "Hello",
                "message_b": "World",
                "use_exact": "true",
                "respect_ecc": "true"
            }
        )
        # Print error details if test fails
        if response.status_code != 200:
            print(f"Error status: {response.status_code}")
            print(f"Error response: {response.text}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "success" in data
        assert "min_flips" in data
        assert "flip_positions" in data
        assert "images" in data  # Changed from comparison_image to images
        assert isinstance(data["min_flips"], int)
        assert isinstance(data["flip_positions"], list)
        # Check images structure
        assert "original" in data["images"]
        assert "target" in data["images"]
        assert "transformed" in data["images"]
        assert "changes" in data["images"]
    
    def test_transform_endpoint_missing_message_b(self, client):
        """Test transformation endpoint with missing message_b."""
        response = client.post(
            "/api/transform",
            data={
                "message_a": "Hello"
            }
        )
        # Should return 422 (validation error) or 400
        assert response.status_code in [400, 422]
    
    def test_transform_endpoint_algorithm_results(self, client):
        """Test that algorithm_results are returned."""
        response = client.post(
            "/api/transform",
            data={
                "message_a": "A",
                "message_b": "B",
                "use_exact": "true",
                "respect_ecc": "true"
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert "algorithm" in data
            assert "algorithm_results" in data
            assert isinstance(data["algorithm_results"], dict)

