"""
Utility functions for model loading and prediction.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np

from model.config import ModelConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelLoader:
    """Handles loading and managing ML model."""

    def __init__(self):
        """Initialize model loader."""
        self.model = None
        self.model_info = None
        self.model_path = None
        self._load_latest_model()

    def _load_latest_model(self) -> None:
        """Load the latest model version."""
        try:
            # Check if latest version info exists
            if os.path.exists(ModelConfig.LATEST_VERSION_PATH):
                latest_info = joblib.load(ModelConfig.LATEST_VERSION_PATH)
                model_path = latest_info["model_path"]
                metadata_path = latest_info["metadata_path"]

                # Log model being loaded
                logger.info(f"Loading model from {model_path}")

                # Load model and metadata
                self.model = joblib.load(model_path)
                self.model_info = joblib.load(metadata_path)
                self.model_path = model_path

                logger.info(
                    f"Model loaded successfully. Version: {self.model_info['version']}"
                )
            else:
                logger.warning(
                    "No model version info found. Please train a model first."
                )
                self.model = None
                self.model_info = {
                    "version": "none",
                    "feature_names": ModelConfig.FEATURE_NAMES,
                }
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def reload_model(self) -> bool:
        """Reload the model (e.g., after a new version is trained)."""
        try:
            self._load_latest_model()
            return True
        except Exception as e:
            logger.error(f"Failed to reload model: {str(e)}")
            return False

    def predict(self, features: Dict[str, float]) -> Tuple[int, str, List[float]]:
        """
        Make a prediction using the loaded model.

        Args:
            features: Dictionary of feature names and values

        Returns:
            Tuple of (prediction class, class label, probabilities)
        """
        if self.model is None:
            raise ValueError("No model loaded. Please train a model first.")

        # Extract features in the correct order
        feature_values = [features[name] for name in ModelConfig.FEATURE_NAMES]
        X = np.array([feature_values])

        # Make prediction
        prediction = int(self.model.predict(X)[0])

        # Get probabilities if available
        probabilities = None
        if hasattr(self.model, "predict_proba"):
            try:
                probabilities = self.model.predict_proba(X)[0].tolist()
            except:
                logger.warning("Could not get prediction probabilities")

        # Get label
        if prediction < len(ModelConfig.PREDICTION_LABELS):
            label = ModelConfig.PREDICTION_LABELS[prediction]
        else:
            label = f"unknown_{prediction}"

        return prediction, label, probabilities

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model."""
        if self.model_info:
            return self.model_info
        return {"status": "No model loaded", "version": "none"}


# Singleton model loader instance
model_loader = ModelLoader()
