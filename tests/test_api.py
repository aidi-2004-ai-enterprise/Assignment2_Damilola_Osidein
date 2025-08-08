# tests/test_api.py
from fastapi.testclient import TestClient
from your_app import app  # Import your FastAPI app
import pytest

client = TestClient(app)

def test_predict_endpoint_valid_input():
    """Test prediction with valid penguin data"""
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_endpoint_invalid_input():
    """Test handling of invalid input"""
    # TODO: Implement this test
    pass

# TODO: Add more tests