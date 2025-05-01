from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, field_validator


class PredictionRequest(BaseModel):
    """Input schema for prediction requests."""

    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

    @field_validator("sepal_length", "sepal_width", "petal_length", "petal_width")
    @classmethod
    def validate_positive(cls, v):
        """Validate that measurements are positive."""
        if v <= 0:
            raise ValueError(f"Measurement must be positive, got {v}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            },
            "properties": {
                "sepal_length": {"description": "Sepal length in cm"},
                "sepal_width": {"description": "Sepal width in cm"},
                "petal_length": {"description": "Petal length in cm"},
                "petal_width": {"description": "Petal width in cm"},
            },
        }
    }


class PredictionResponse(BaseModel):
    """Output schema for prediction responses."""

    prediction: int
    prediction_label: str
    request_id: str = str(uuid4())
    model_version: str
    probabilities: Optional[List[float]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "prediction": 0,
                "prediction_label": "setosa",
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "model_version": "1.0.0",
                "probabilities": [0.95, 0.04, 0.01],
            },
            "properties": {
                "prediction": {"description": "Predicted class (numeric)"},
                "prediction_label": {"description": "Predicted class (label)"},
                "request_id": {"description": "Unique request identifier"},
                "model_version": {"description": "Model version used for prediction"},
                "probabilities": {
                    "description": "Prediction probabilities for each class"
                },
            },
        }
    }
