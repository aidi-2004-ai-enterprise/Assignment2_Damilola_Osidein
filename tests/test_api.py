import os
import pytest
import xgboost as xgb
import numpy as np
from fastapi.testclient import TestClient
from main import app, FEATURE_NAMES

# Set test mode
os.environ["TEST_MODE"] = "1"

@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

def test_model_prediction():
    """Test XGBoost model prediction with known penguin data"""
    model = xgb.Booster()
    model_path = os.path.join(os.path.dirname(__file__), "..", "penguin_model.json")
    model.load_model(model_path)
    sample_data = [[39.1, 18.7, 181, 3750]]
    dmatrix = xgb.DMatrix(sample_data, feature_names=FEATURE_NAMES)
    prediction = model.predict(dmatrix)
    predicted_class = int(np.argmax(prediction[0]))
    assert predicted_class in [0, 1, 2]

def test_predict_endpoint_valid_input(client):
    """Test prediction with valid penguin data"""
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert "prediction" in response.json()
    assert response.json()["prediction"] in ["Adelie", "Chinstrap", "Gentoo"]

def test_predict_endpoint_missing_field(client):
    """Test handling of missing input field"""
    sample_data = {
        "bill_length_mm": 39.1,
        "flipper_length_mm": 181,
        "body_mass_g": 3750
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

def test_predict_endpoint_invalid_type(client):
    """Test handling of invalid data type"""
    sample_data = {
        "bill_length_mm": "invalid",
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

def test_predict_endpoint_negative_value(client):
    """Test handling of out-of-range (negative) value"""
    sample_data = {
        "bill_length_mm": -39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

def test_predict_endpoint_empty_request(client):
    """Test handling of empty request"""
    response = client.post("/predict", json={})
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"