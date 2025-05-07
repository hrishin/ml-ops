"""
FastAPI application for serving Iris classifier predictions.
"""

import logging
import time

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status, APIRouter
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

# Define API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Health check endpoint
@api_router.get("/health", status_code=status.HTTP_200_OK)
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
@api_router.get("/model/info", status_code=status.HTTP_200_OK)
async def model_info():
    """Get information about the currently loaded model."""
    return model_loader.get_model_info()

# Reload model endpoint
@api_router.post("/model/reload", status_code=status.HTTP_200_OK)
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
@api_router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a prediction with the Iris classifier model.
    """
    try:
        logger.info(f"Prediction request: {request}")

        if model_loader.model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please train a model first.",
            )

        prediction, label, probabilities = model_loader.predict(request.dict())

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

# Root endpoint for versioned API
@api_router.get("/")
async def api_root():
    return {
        "message": "Iris Classifier API - v1",
        "endpoints": {
            "/predict": "Make a prediction (POST)",
            "/health": "Health check (GET)",
            "/model/info": "Get model information (GET)",
            "/model/reload": "Reload model from disk (POST)",
        },
    }

# Add router to app
app.include_router(api_router)

# Root endpoint without version
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Iris Classifier API",
        "docs": "/docs",
        "versioned_entrypoint": "/api/v1/",
    }

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

# Run the app
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
