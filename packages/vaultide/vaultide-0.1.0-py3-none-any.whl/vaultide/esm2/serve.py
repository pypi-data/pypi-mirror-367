"""
ESM-2 FastAPI server for running predictions.

This module provides a FastAPI server that loads ESM-2 LoRA models
and serves predictions via HTTP endpoints.
"""

import logging
import os
from datetime import datetime
from typing import List, Optional, Union

from vaultide.config import get_lora_base_path

# Configure logging
logger = logging.getLogger("vaultide")


def serve_esm2(
    lora_name: str,
    lora_strength: float = 1.0,
    host: str = "127.0.0.1",
    port: int = 8000,
    verbose: bool = False,
) -> None:
    """
    Start FastAPI server for ESM-2 predictions.

    Args:
        lora_name: Name of the LoRA model to use
        lora_strength: LoRA strength (0.0 to 2.0, default: 1.0)
        host: Host to bind server to (default: 127.0.0.1)
        port: Port to bind server to (default: 8000)
        verbose: Show verbose server logs
    """
    logger.info(f"Starting ESM-2 prediction server with LoRA: {lora_name}")
    logger.info(f"LoRA strength: {lora_strength}")
    logger.info(f"Server will run on: http://{host}:{port}")

    # Lazy import of FastAPI and uvicorn
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn
    except ImportError as e:
        logger.error(f"Missing dependencies for serve command: {e}")
        logger.error("Please install FastAPI and uvicorn: pip install fastapi uvicorn")
        return None

    # Lazy import of inference modules
    from .inference import (
        load_lora_model,
        validate_sequence,
        process_model_outputs,
        calculate_confidence,
    )

    # Validate LoRA exists
    lora_path = os.path.join(get_lora_base_path("esm2"), lora_name)
    if not os.path.exists(lora_path):
        logger.error(f"LoRA model not found: {lora_name}")
        logger.error("Available LoRAs can be listed with: vaultide list loras esm2")
        return None

    # Load model once at startup
    try:
        logger.info("Loading model...")
        model, tokenizer, base_model_name = load_lora_model(lora_name, lora_strength)
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None

    # Define request/response models
    class PredictionRequest(BaseModel):
        sequence: str
        lora_strength: Optional[float] = None
        full_probabilities: Optional[bool] = False

    class PredictionResponse(BaseModel):
        prediction: Union[float, List[float]]
        confidence: Optional[float]
        base_model: str
        lora_name: str
        lora_strength: float
        sequence: str
        timestamp: str

    # Create FastAPI app
    app = FastAPI(
        title="Vaultide ESM-2 Prediction API",
        description="API for running protein sequence predictions using trained ESM-2 LoRA models",
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

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Vaultide ESM-2 Prediction API",
            "version": "1.0.0",
            "model": lora_name,
            "base_model": base_model_name,
            "lora_strength": lora_strength,
            "endpoints": {
                "/predict": "POST - Run prediction on protein sequence",
                "/health": "GET - Health check",
                "/model-info": "GET - Model information",
            },
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "model_loaded": True}

    @app.get("/model-info")
    async def model_info():
        """Get information about the loaded model."""
        return {
            "lora_name": lora_name,
            "base_model": base_model_name,
            "lora_strength": lora_strength,
            "device": str(next(model.parameters()).device),
        }

    @app.post("/predict", response_model=PredictionResponse)
    async def predict(request: PredictionRequest):
        """Run prediction on a protein sequence."""
        try:
            # Validate sequence
            sequence = request.sequence.upper()
            if not validate_sequence(sequence):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid protein sequence. Only standard amino acids (ACDEFGHIKLMNPQRSTVWY) are allowed.",
                )

            # Use request lora_strength if provided, otherwise use default
            request_lora_strength = (
                request.lora_strength
                if request.lora_strength is not None
                else lora_strength
            )

            # Tokenize sequence
            inputs = tokenizer(
                sequence,
                return_tensors="pt",
                truncation=True,
                max_length=1024,
                padding=True,
            )

            # Move inputs to device
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Run inference
            import torch

            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                # Use default value if full_probabilities is None
                full_probabilities = (
                    request.full_probabilities
                    if request.full_probabilities is not None
                    else False
                )
                prediction = process_model_outputs(logits, full_probabilities)

            # Calculate confidence
            confidence = calculate_confidence(prediction)

            return PredictionResponse(
                prediction=prediction,
                confidence=confidence,
                base_model=base_model_name,
                lora_name=lora_name,
                lora_strength=request_lora_strength,
                sequence=sequence,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Start server
    logger.info(f"Starting server on http://{host}:{port}")
    logger.info("Press Ctrl+C to stop the server")

    uvicorn.run(app, host=host, port=port, log_level="info" if verbose else "warning")
