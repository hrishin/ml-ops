#!/usr/bin/env python3
"""
Training script for Iris dataset classification model.
This script loads data, preprocesses it, trains a model, and saves the pipeline.
"""

import logging
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from model.config import ModelConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_artifacts_dir():
    """Create artifacts directory if it doesn't exist."""
    os.makedirs(ModelConfig.ARTIFACTS_DIR, exist_ok=True)

def load_data():
    """Load iris dataset."""
    logger.info("Loading Iris dataset")
    # Option 1: Load from sklearn
    if not os.path.exists(ModelConfig.DATA_PATH):
        X, y = load_iris(return_X_y=True)
        feature_names = load_iris().feature_names
        target_names = load_iris().target_names
        
        # Save to CSV for future runs
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        df.to_csv(ModelConfig.DATA_PATH, index=False)
        
        return X, y, feature_names, target_names
    
    # Option 2: Load from CSV
    logger.info(f"Loading data from {ModelConfig.DATA_PATH}")
    df = pd.read_csv(ModelConfig.DATA_PATH)
    
    y = df['target'].values
    X = df.drop('target', axis=1).values
    feature_names = df.drop('target', axis=1).columns.tolist()
    target_names = np.unique(y).tolist()
    
    return X, y, feature_names, target_names

def build_pipeline():
    """Create sklearn pipeline with preprocessing and model."""
    logger.info("Building machine learning pipeline")
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(max_iter=200, random_state=42))
    ])
    
    return pipeline

def train_model():
    """Train the model and save pipeline artifacts."""
    # Create artifacts directory
    create_artifacts_dir()
    
    # Load data
    X, y, feature_names, target_names = load_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Build and train pipeline
    pipeline = build_pipeline()
    logger.info("Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info(f"Classification report:\n{classification_report(y_test, y_pred, target_names=load_iris().target_names)}")
    
    # Create model metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_version = f"{ModelConfig.VERSION_PREFIX}.{timestamp}"
    model_info = {
        "version": model_version,
        "accuracy": float(accuracy),
        "feature_names": feature_names,
        "target_names": target_names.tolist() if hasattr(target_names, 'tolist') else target_names,
        "created_at": datetime.now().isoformat(),
        "model_type": "logistic_regression"
    }
    
    # Save pipeline and metadata
    model_path = os.path.join(ModelConfig.ARTIFACTS_DIR, f"model_pipeline_{model_version}.joblib")
    metadata_path = os.path.join(ModelConfig.ARTIFACTS_DIR, f"model_metadata_{model_version}.joblib")
    
    logger.info(f"Saving model to {model_path}")
    joblib.dump(pipeline, model_path)
    joblib.dump(model_info, metadata_path)
    
    # Save latest version info
    latest_info = {
        "latest_version": model_version,
        "model_path": model_path,
        "metadata_path": metadata_path
    }
    joblib.dump(latest_info, ModelConfig.LATEST_VERSION_PATH)
    
    logger.info(f"Model training completed. Version: {model_version}")
    return model_path, metadata_path, model_info

if __name__ == "__main__":
    train_model()