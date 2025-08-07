"""
ESMC Batch Inference Module

This module provides batch inference utilities for the ESMC model using the esm Python package.
"""

import logging
import os
import pandas as pd
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import torch

from .inference import predict_batch, get_model_info
from vaultide.config import get_lora_base_path

# Configure logging
logger = logging.getLogger("vaultide")

# Use CUDA if available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def validate_input_csv(
    input_csv: str, sequence_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate input CSV file and extract metadata.

    Args:
        input_csv: Path to input CSV file
        sequence_column: Name of sequence column (auto-detected if None)

    Returns:
        Dictionary containing validation results and metadata

    Raises:
        ValueError: If CSV is invalid or missing required columns
    """
    if not os.path.exists(input_csv):
        raise ValueError(f"Input CSV file not found: {input_csv}")

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        raise ValueError(f"Could not read CSV file {input_csv}: {e}")

    if len(df) == 0:
        raise ValueError("CSV file is empty")

    # Auto-detect sequence column if not provided
    if sequence_column is None:
        available_columns = set(df.columns)
        priority_columns = ["sequence", "window", "protein_sequence", "seq"]

        for col in priority_columns:
            if col in available_columns:
                sequence_column = col
                break
        else:
            # Try to find any column that might contain sequences
            potential_columns = [
                col
                for col in available_columns
                if any(
                    keyword in col.lower()
                    for keyword in ["sequence", "seq", "window", "protein"]
                )
            ]
            if potential_columns:
                sequence_column = potential_columns[0]
            else:
                raise ValueError(
                    "Could not detect sequence column. Please specify --sequence-column. "
                    f"Available columns: {list(available_columns)}"
                )

    if sequence_column not in df.columns:
        raise ValueError(
            f"Sequence column '{sequence_column}' not found in CSV. "
            f"Available columns: {list(df.columns)}"
        )

    # Validate sequences
    sequences = df[sequence_column].astype(str)
    valid_sequences = sequences.str.strip().str.len() > 0
    invalid_count = (~valid_sequences).sum()

    if invalid_count > 0:
        logger.warning(f"Found {invalid_count} invalid sequences (empty or whitespace)")

    # Calculate file hash
    with open(input_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    return {
        "file_path": input_csv,
        "file_size_bytes": os.path.getsize(input_csv),
        "file_hash": file_hash,
        "total_rows": len(df),
        "valid_rows": valid_sequences.sum(),
        "invalid_rows": invalid_count,
        "sequence_column": sequence_column,
        "available_columns": list(df.columns),
    }


def process_batch_predictions(
    input_csv: str,
    output_dir: str,
    lora_name: str,
    sequence_column: Optional[str] = None,
    lora_strength: float = 1.0,
    full_probabilities: bool = False,
    batch_size: int = 32,
    max_length: int = 1024,
) -> Dict[str, Any]:
    """
    Process batch predictions on CSV data.

    Args:
        input_csv: Path to input CSV file
        output_dir: Directory to save output files
        lora_name: Name of the LoRA model to use
        sequence_column: Name of sequence column (auto-detected if None)
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        full_probabilities: Whether to return full probability distribution
        batch_size: Batch size for processing
        max_length: Maximum sequence length for tokenization

    Returns:
        Dictionary containing processing results and metadata

    Raises:
        ValueError: If inputs are invalid
        FileNotFoundError: If LoRA model doesn't exist
    """
    start_time = datetime.now()

    # Validate inputs
    if not os.path.exists(input_csv):
        raise ValueError(f"Input CSV file not found: {input_csv}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

    # Validate input CSV
    validation_info = validate_input_csv(input_csv, sequence_column)
    logger.info(
        f"Input validation completed: {validation_info['valid_rows']} valid sequences"
    )

    # Load input data
    df = pd.read_csv(input_csv)
    sequences = df[validation_info["sequence_column"]].astype(str).str.strip()
    valid_mask = sequences.str.len() > 0

    # Filter to valid sequences
    valid_df = df[valid_mask].copy()
    valid_sequences = sequences[valid_mask].tolist()

    if len(valid_sequences) == 0:
        raise ValueError("No valid sequences found in input file")

    logger.info(f"Processing {len(valid_sequences)} valid sequences")

    # Run batch predictions
    try:
        predictions = predict_batch(
            sequences=valid_sequences,
            lora_name=lora_name,
            lora_strength=lora_strength,
            full_probabilities=full_probabilities,
            max_length=max_length,
            batch_size=batch_size,
        )
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise

    # Create output DataFrame
    output_df = valid_df.copy()

    # Add prediction columns
    output_df["prediction"] = [pred["prediction"] for pred in predictions]
    output_df["confidence"] = [pred["confidence"] for pred in predictions]

    if full_probabilities:
        # Add individual class probabilities
        for i in range(2):  # Binary classification
            output_df[f"prediction_class_{i}"] = [
                pred["probabilities"][f"class_{i}"] for pred in predictions
            ]
    else:
        # Add positive class probability
        output_df["positive_probability"] = [
            pred["positive_probability"] for pred in predictions
        ]

    # Save predictions CSV
    predictions_csv = os.path.join(output_dir, "predictions.csv")
    output_df.to_csv(predictions_csv, index=False)
    logger.info(f"Saved predictions to: {predictions_csv}")

    # Generate metadata
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Get model info
    try:
        model_info = get_model_info(lora_name)
    except Exception as e:
        logger.warning(f"Could not get model info: {e}")
        model_info = {"lora_name": lora_name}

    # Create metadata
    metadata: Dict[str, Any] = {
        "metadata_version": "1.0",
        "generation_timestamp": end_time.isoformat(),
        "metadata_id": uuid.uuid4().hex,
        "input_file": validation_info,
        "model": {
            "lora_name": lora_name,
            "lora_strength": lora_strength,
            "full_probabilities": full_probabilities,
            "batch_size": batch_size,
            "max_length": max_length,
        },
        "processing": {
            "processing_time_seconds": processing_time,
            "total_predictions": len(predictions),
            "device": DEVICE,
        },
        "output_files": {
            "predictions_csv": predictions_csv,
            "metadata_json": os.path.join(output_dir, "metadata.json"),
        },
    }

    # Add model info if available
    if "base_model" in model_info:
        metadata["model"]["base_model"] = model_info["base_model"]
    if "training_metadata" in model_info:
        metadata["model"]["training_metadata"] = model_info["training_metadata"]

    # Save metadata
    metadata_json = os.path.join(output_dir, "metadata.json")
    with open(metadata_json, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to: {metadata_json}")

    # Calculate output file hashes
    output_hashes = {}
    for filename in ["predictions.csv", "metadata.json"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                output_hashes[filename] = hashlib.sha256(f.read()).hexdigest()

    metadata["output_files"]["file_hashes"] = output_hashes

    # Update metadata file with hashes
    with open(metadata_json, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Batch processing completed in {processing_time:.2f} seconds")
    logger.info(f"Results saved to: {output_dir}")

    return {
        "predictions_csv": predictions_csv,
        "metadata_json": metadata_json,
        "processing_time_seconds": processing_time,
        "total_predictions": len(predictions),
        "metadata": metadata,
    }


def validate_batch_inputs(
    input_csv: str,
    output_dir: str,
    lora_name: str,
    sequence_column: Optional[str] = None,
    lora_strength: float = 1.0,
    batch_size: int = 32,
) -> Dict[str, Any]:
    """
    Validate all inputs for batch prediction.

    Args:
        input_csv: Path to input CSV file
        output_dir: Directory to save output files
        lora_name: Name of the LoRA model to use
        sequence_column: Name of sequence column (auto-detected if None)
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        batch_size: Batch size for processing

    Returns:
        Dictionary containing validation results

    Raises:
        ValueError: If any inputs are invalid
    """
    validation_results: Dict[str, Any] = {}

    # Validate input CSV
    try:
        csv_validation = validate_input_csv(input_csv, sequence_column)
        validation_results["csv_validation"] = csv_validation
        logger.info("✓ Input CSV validation passed")
    except Exception as e:
        validation_results["csv_validation"] = {"error": str(e)}
        raise ValueError(f"Input CSV validation failed: {e}")

    # Validate output directory
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"✓ Created output directory: {output_dir}")
        else:
            logger.info(f"✓ Output directory exists: {output_dir}")
        validation_results["output_dir"] = output_dir
    except Exception as e:
        raise ValueError(f"Output directory validation failed: {e}")

    # Validate LoRA model
    try:
        lora_path = os.path.join(get_lora_base_path("esmc"), lora_name)
        if not os.path.exists(lora_path):
            raise FileNotFoundError(f"LoRA model not found: {lora_path}")

        # Check for required files
        required_files = ["model.pt", "base_model.pt"]

        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(lora_path, file)):
                missing_files.append(file)

        if missing_files:
            raise FileNotFoundError(f"Missing required files: {missing_files}")

        validation_results["lora_validation"] = {
            "lora_name": lora_name,
            "lora_path": lora_path,
            "status": "valid",
        }
        logger.info("✓ LoRA model validation passed")
    except Exception as e:
        validation_results["lora_validation"] = {"error": str(e)}
        raise ValueError(f"LoRA model validation failed: {e}")

    # Validate LoRA strength
    if not 0.0 <= lora_strength <= 2.0:
        raise ValueError("LoRA strength must be between 0.0 and 2.0")
    validation_results["lora_strength"] = lora_strength

    # Validate batch size
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")
    validation_results["batch_size"] = batch_size

    logger.info("✓ All validations passed")
    return validation_results
