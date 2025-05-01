"""
Configuration settings for model training and serving.
"""

import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class ModelConfig:
    """Configuration for model training and serving."""
    
    # Directories
    ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    
    # Files
    DATA_PATH = os.path.join(DATA_DIR, "iris.csv")
    LATEST_VERSION_PATH = os.path.join(ARTIFACTS_DIR, "latest_version.joblib")
    
    # Model versioning
    VERSION_PREFIX = "1.0"
    
    # Model serving
    MODEL_NAME = "iris_classifier"
    DEFAULT_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model_pipeline_latest.joblib")
    PREDICTION_LABELS = ["setosa", "versicolor", "virginica"]
    
    # Feature names (for API validation)
    FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]