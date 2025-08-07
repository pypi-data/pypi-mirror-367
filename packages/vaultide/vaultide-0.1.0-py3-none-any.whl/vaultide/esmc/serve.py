"""
ESMC Serve Module

This module provides serving utilities for the ESMC model using the esm Python package.
"""

import logging
import os
from typing import Dict, Any, Optional
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from .inference import predict_sequence, load_model_and_tokenizer

# Configure logging
logger = logging.getLogger("vaultide")

# Use CUDA if available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""

    sequence: str = Field(..., description="Protein sequence to predict on")
    lora_strength: float = Field(
        1.0, ge=0.0, le=2.0, description="LoRA strength (0.0 to 2.0)"
    )
    full_probabilities: bool = Field(
        False, description="Return full probability distribution"
    )


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""

    prediction: int = Field(..., description="Model prediction (0 or 1)")
    confidence: float = Field(..., description="Prediction confidence")
    positive_probability: Optional[float] = Field(
        None, description="Positive class probability"
    )
    probabilities: Optional[Dict[str, float]] = Field(
        None, description="Full probability distribution"
    )
    sequence: str = Field(..., description="Input sequence")
    sequence_length: int = Field(..., description="Sequence length")
    lora_name: str = Field(..., description="LoRA model name")
    lora_strength: float = Field(..., description="LoRA strength used")
    base_model: str = Field(..., description="Base model name")
    device: str = Field(..., description="Device used for inference")


class ModelInfoResponse(BaseModel):
    """Response model for model info endpoint."""

    lora_name: str = Field(..., description="LoRA model name")
    base_model: str = Field(..., description="Base model name")
    lora_path: str = Field(..., description="LoRA model path")
    file_sizes: Dict[str, int] = Field(..., description="File sizes in bytes")
    total_size_bytes: int = Field(..., description="Total model size in bytes")
    training_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Training metadata"
    )


def create_app(lora_name: str, lora_strength: float = 1.0) -> FastAPI:
    """
    Create FastAPI application for ESMC model serving.

    Args:
        lora_name: Name of the LoRA model to serve
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)

    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="ESMC Prediction API",
        description="API for protein sequence prediction using ESMC model with ESM",
        version="1.0.0",
    )

    # Global variables for model and alphabet
    model = None
    alphabet = None
    base_model_name = None

    @app.on_event("startup")
    async def startup_event():
        """Load model on startup."""
        nonlocal model, alphabet, base_model_name

        try:
            logger.info(f"Loading ESMC model: {lora_name}")
            model, alphabet, base_model_name = load_model_and_tokenizer(
                lora_name, lora_strength
            )
            logger.info(f"Model loaded successfully on device: {DEVICE}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    @app.get("/")
    async def root():
        """API information and available endpoints."""
        return {
            "name": "ESMC Prediction API",
            "version": "1.0.0",
            "description": "API for protein sequence prediction using ESMC model with ESM",
            "endpoints": {
                "GET /": "API information (this endpoint)",
                "GET /health": "Health check",
                "GET /model-info": "Model information",
                "POST /predict": "Run prediction on protein sequence",
            },
            "model": {
                "lora_name": lora_name,
                "lora_strength": lora_strength,
                "base_model": base_model_name,
                "device": DEVICE,
            },
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        if model is None or alphabet is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        return {
            "status": "healthy",
            "model_loaded": model is not None,
            "device": DEVICE,
            "lora_name": lora_name,
            "lora_strength": lora_strength,
        }

    @app.get("/model-info", response_model=ModelInfoResponse)
    async def get_model_info():
        """Get information about the loaded model."""
        try:
            info = get_model_info(lora_name)
            return ModelInfoResponse(**info)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get model info: {e}"
            )

    @app.post("/predict", response_model=PredictionResponse)
    async def predict(request: PredictionRequest):
        """Run prediction on a protein sequence."""
        if model is None or alphabet is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        try:
            # Validate sequence
            if not request.sequence or not isinstance(request.sequence, str):
                raise HTTPException(
                    status_code=400, detail="Sequence must be a non-empty string"
                )

            sequence = request.sequence.strip()
            if not sequence:
                raise HTTPException(status_code=400, detail="Sequence cannot be empty")

            # Run prediction
            result = predict_sequence(
                sequence=sequence,
                lora_name=lora_name,
                lora_strength=request.lora_strength,
                full_probabilities=request.full_probabilities,
            )

            # Create response
            response_data = {
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "sequence": result["sequence"],
                "sequence_length": result["sequence_length"],
                "lora_name": result["lora_name"],
                "lora_strength": result["lora_strength"],
                "base_model": result["base_model"],
                "device": result["device"],
            }

            if request.full_probabilities:
                response_data["probabilities"] = result["probabilities"]
            else:
                response_data["positive_probability"] = result["positive_probability"]

            return PredictionResponse(**response_data)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


def serve_esmc(
    lora_name: str,
    lora_strength: float = 1.0,
    host: str = "127.0.0.1",
    port: int = 8000,
    verbose: bool = False,
):
    """
    Start ESMC prediction server.

    Args:
        lora_name: Name of the LoRA model to serve
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        host: Host to bind server to
        port: Port to bind server to
        verbose: Whether to enable verbose logging

    Raises:
        ValueError: If inputs are invalid
        FileNotFoundError: If LoRA model doesn't exist
    """
    # Validate inputs
    if not lora_name:
        raise ValueError("LoRA name cannot be empty")

    if not 0.0 <= lora_strength <= 2.0:
        raise ValueError("LoRA strength must be between 0.0 and 2.0")

    # Validate LoRA model exists
    from vaultide.config import get_lora_base_path

    lora_path = os.path.join(get_lora_base_path("esmc"), lora_name)
    if not os.path.exists(lora_path):
        raise FileNotFoundError(f"LoRA model not found: {lora_path}")

    # Set logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("STARTING ESMC PREDICTION SERVER")
    logger.info(f"LoRA model: {lora_name}")
    logger.info(f"LoRA strength: {lora_strength}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Device: {DEVICE}")
    logger.info("=" * 60)

    # Create FastAPI app
    app = create_app(lora_name, lora_strength)

    # Start server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="debug" if verbose else "info",
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise
