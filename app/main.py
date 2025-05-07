"""
FastAPI application for serving Iris classifier predictions.
"""

import logging
import time

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import PredictionRequest, PredictionResponse
from app.utils import model_loader

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Iris Classifier API",
    description="API for making predictions with the Iris flower classifier model",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    if model_loader.model is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "message": "Model not loaded"},
        )
    return {
        "status": "healthy",
        "model_version": model_loader.model_info.get("version", "unknown"),
    }


# Model info endpoint
@app.get("/model/info", status_code=status.HTTP_200_OK)
async def model_info():
    """Get information about the currently loaded model."""
    return model_loader.get_model_info()


# Reload model endpoint
@app.post("/model/reload", status_code=status.HTTP_200_OK)
async def reload_model():
    """Reload the model from disk."""
    success = model_loader.reload_model()
    if not success:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Failed to reload model"},
        )
    return {
        "status": "success",
        "message": "Model reloaded",
        "model_info": model_loader.get_model_info(),
    }


# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a prediction with the Iris classifier model.

    Args:
        request: Input features for prediction

    Returns:
        Prediction result with class and metadata
    """
    try:
        logger.info(f"Prediction request: {request}")
        # import pdb; pdb.set_trace()

        # Check if model is loaded
        if model_loader.model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please train a model first.",
            )

        # Make prediction
        prediction, label, probabilities = model_loader.predict(request.dict())

        # Create response
        response = PredictionResponse(
            prediction=prediction,
            prediction_label=label,
            model_version=model_loader.model_info.get("version", "unknown"),
            probabilities=probabilities,
        )

        logger.info(f"Prediction result: {response}")
        return response

    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error making prediction: {str(e)}",
        )


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Iris Classifier API",
        "endpoints": {
            "/predict": "Make a prediction (POST)",
            "/health": "Health check (GET)",
            "/model/info": "Get model information (GET)",
            "/model/reload": "Reload model from disk (POST)",
            "/docs": "API documentation",
        },
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
