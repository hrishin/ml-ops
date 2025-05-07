"""
Step definitions for predict.feature
"""
import os
from contextlib import contextmanager
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app.main import app
from app.utils import model_loader
from model.config import ModelConfig
from model.train import train_model

# Load scenarios from feature file
scenarios("../predict.feature")

# # Create test client
# client = TestClient(app)


@contextmanager
def temp_model_loader():
    """Context manager to temporarily modify model loader for testing."""
    original_model = model_loader.model
    original_model_info = model_loader.model_info
    original_model_path = model_loader.model_path

    try:
        yield model_loader
    finally:
        model_loader.model = original_model
        model_loader.model_info = original_model_info
        model_loader.model_path = original_model_path


@pytest.fixture()
def test_client():
    """Create a test client for the FastAPI application."""
    client = TestClient(app)
    yield client


@pytest.fixture()
def request_data():
    """Fixture to store request data between steps."""
    return {}


@given("the ML model is trained and available")
def ensure_model_is_trained():
    """Ensure model is trained for tests."""
    # Check if model exists, if not, train it
    if not os.path.exists(ModelConfig.LATEST_VERSION_PATH):
        model_path, metadata_path, _ = train_model()
        assert os.path.exists(model_path), f"Model was not created at {model_path}"

    # Ensure model is loaded
    if model_loader.model is None:
        model_loader.reload_model()

    assert model_loader.model is not None, "Model could not be loaded"


@when(parsers.parse("I provide the following measurements:\n{measurements}"))
def provide_measurements(request_data, measurements):
    """Parse measurement table to dict."""
    # Parse table using pandas for convenience
    df = pd.read_csv(StringIO(measurements), sep="|", skipinitialspace=True)
    df = df.dropna(axis=1, how="all")  # Remove empty columns
    df.columns = df.columns.str.strip()

    # Convert to dict for request
    data = df.iloc[0].to_dict()
    request_data.update(data)
    print(f"sending request {request_data}")


@when("I send a prediction request")
def send_prediction_request(request_data, test_client):
    """Send prediction request to API."""
    # Store response in request_data for use in then steps
    response = test_client.post(
        "/api/v1/predict", headers={"Content-Type": "application/json"}, json=request_data
    )
    print(f"response {response.json()}")

    request_data["response"] = response
    request_data["status_code"] = response.status_code

    # Try to parse response body if JSON
    try:
        request_data["response_json"] = response.json()
    except:
        request_data["response_json"] = None


@when("I check the API health status")
def check_health_status(request_data, test_client):
    """Check API health status."""
    response = test_client.get("/api/v1/health")
    request_data["response"] = response
    request_data["status_code"] = response.status_code

    try:
        request_data["response_json"] = response.json()
    except:
        request_data["response_json"] = None


@then("I should receive a successful response")
def check_successful_response(request_data):
    """Check response is successful."""
    assert (
        request_data["status_code"] == 200
    ), f"Expected status code 200, got {request_data['status_code']}"
    assert request_data["response_json"] is not None, "Response is not valid JSON"


@then("I should receive an error response")
def check_error_response(request_data):
    """Check response is an error."""
    assert (
        request_data["status_code"] >= 400
    ), f"Expected error status code, got {request_data['status_code']}"
    assert request_data["response_json"] is not None, "Response is not valid JSON"


@then(parsers.parse('the prediction should be "{prediction}"'))
def check_prediction(request_data, prediction):
    """Check prediction value."""
    assert (
        request_data["response_json"]["prediction_label"] == prediction
    ), f"Expected prediction '{prediction}', got '{request_data['response_json']['prediction_label']}'"


@then("the model version should be available in the response")
def check_model_version(request_data):
    """Check model version is in response."""
    assert (
        "model_version" in request_data["response_json"]
    ), "Model version not in response"
    assert request_data["response_json"]["model_version"], "Model version is empty"


@then(parsers.parse('the error message should mention "{text}"'))
def check_error_message(request_data, text):
    """Check error message contains text."""
    assert "detail" in request_data["response_json"], "No error detail in response"
    assert text in str(
        request_data["response_json"]["detail"]
    ), f"Expected '{text}' in error message, got '{request_data['response_json']['detail']}'"


@then(parsers.parse('the health check should report "{status}"'))
def check_health_status_value(request_data, status):
    """Check health check status."""
    assert (
        "status" in request_data["response_json"]
    ), "No status in health check response"
    assert (
        request_data["response_json"]["status"] == status
    ), f"Expected status '{status}', got '{request_data['response_json']['status']}'"
