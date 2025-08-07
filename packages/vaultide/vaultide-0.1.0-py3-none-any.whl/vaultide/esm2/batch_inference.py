"""
ESM-2 batch inference module for Vaultide.

This module provides functionality to run batch inference on CSV files
and generate predictions with metadata for compliance and audit purposes.
"""

import logging
import os
import sys
import json
import pandas as pd
import torch
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import uuid

from .inference import (
    load_lora_model,
    validate_sequence,
    process_model_outputs,
    calculate_confidence,
)
from vaultide.config import get_lora_base_path

logger = logging.getLogger("vaultide")


def auto_detect_sequence_column(df: pd.DataFrame) -> str:
    """
    Auto-detect sequence column in DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        str: Name of the sequence column

    Raises:
        ValueError: If no sequence column can be detected
    """
    # Priority order for sequence column detection
    sequence_columns = ["sequence", "window", "protein_sequence", "seq", "protein_seq"]

    # Check for exact matches first
    for col in sequence_columns:
        if col in df.columns:
            logger.info(f"Auto-detected sequence column: {col}")
            return col

    # Check for partial matches
    for col in df.columns:
        col_lower = col.lower()
        if any(
            keyword in col_lower for keyword in ["sequence", "seq", "window", "protein"]
        ):
            logger.info(f"Auto-detected sequence column: {col}")
            return col

    raise ValueError(
        "Could not detect sequence column. Please specify --sequence-column. "
        f"Expected columns: {sequence_columns} or similar. "
        f"Available columns: {list(df.columns)}"
    )


def validate_csv_data(
    df: pd.DataFrame, sequence_column: str
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate CSV data and return cleaned DataFrame with validation errors.

    Args:
        df: Input DataFrame
        sequence_column: Name of the sequence column

    Returns:
        Tuple of (cleaned_df, validation_errors)
    """
    validation_errors = []

    # Check if sequence column exists
    if sequence_column not in df.columns:
        raise ValueError(f"Sequence column '{sequence_column}' not found in CSV")

    # Convert sequences to string and validate
    df[sequence_column] = df[sequence_column].astype(str)

    # Validate each sequence
    for idx, sequence in enumerate(df[sequence_column]):
        if pd.isna(sequence) or sequence.strip() == "":
            validation_errors.append(f"Row {idx + 1}: Empty sequence")
            continue

        if not validate_sequence(sequence):
            validation_errors.append(
                f"Row {idx + 1}: Invalid sequence '{sequence[:50]}...' "
                "(only standard amino acids ACDEFGHIKLMNPQRSTVWY allowed)"
            )

    # Remove rows with validation errors
    if validation_errors:
        logger.warning(f"Found {len(validation_errors)} validation errors")
        for error in validation_errors:
            logger.warning(error)

    # Filter out invalid sequences - check for empty strings and invalid sequences
    def is_valid_sequence(seq):
        if pd.isna(seq) or seq.strip() == "":
            return False
        return validate_sequence(seq)

    valid_mask = df[sequence_column].apply(is_valid_sequence)
    df_cleaned = df[valid_mask].copy()

    if len(df_cleaned) == 0:
        raise ValueError("No valid sequences found in CSV file")

    logger.info(f"Processing {len(df_cleaned)} valid sequences out of {len(df)} total")

    return df_cleaned, validation_errors


def generate_metadata(
    lora_name: str,
    input_csv_path: str,
    output_dir: str,
    sequence_column: str,
    lora_strength: float,
    full_probabilities: bool,
    batch_size: int,
    validation_errors: List[str],
    processing_stats: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate metadata for compliance and audit purposes.

    Args:
        lora_name: Name of the LoRA model used
        input_csv_path: Path to input CSV file
        output_dir: Output directory path
        sequence_column: Name of sequence column used
        lora_strength: LoRA strength parameter
        full_probabilities: Whether full probabilities were returned
        batch_size: Batch size used for processing
        validation_errors: List of validation errors encountered
        processing_stats: Processing statistics

    Returns:
        Dict containing metadata
    """

    # Calculate file hashes for integrity
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        if not os.path.exists(file_path):
            return "file_not_found"

        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    # Get LoRA model info
    lora_path = os.path.join(get_lora_base_path("esm2"), lora_name)
    lora_config_path = os.path.join(lora_path, "adapter_config.json")

    metadata = {
        "metadata_version": "1.0",
        "generation_timestamp": datetime.now().isoformat(),
        "metadata_id": str(uuid.uuid4()),
        # Input information
        "input_file": {
            "path": input_csv_path,
            "hash": calculate_file_hash(input_csv_path),
            "size_bytes": os.path.getsize(input_csv_path)
            if os.path.exists(input_csv_path)
            else 0,
            "sequence_column": sequence_column,
            "total_rows": processing_stats.get("total_rows", 0),
            "valid_rows": processing_stats.get("valid_rows", 0),
            "invalid_rows": processing_stats.get("invalid_rows", 0),
        },
        # Model information
        "model": {
            "lora_name": lora_name,
            "lora_path": lora_path,
            "lora_config_hash": calculate_file_hash(lora_config_path),
            "lora_strength": lora_strength,
            "full_probabilities": full_probabilities,
            "batch_size": batch_size,
        },
        # Output information
        "output": {
            "directory": output_dir,
            "output_csv": os.path.join(output_dir, "predictions.csv"),
            "metadata_file": os.path.join(output_dir, "metadata.json"),
        },
        # Processing information
        "processing": {
            "start_time": processing_stats.get("start_time"),
            "end_time": processing_stats.get("end_time"),
            "processing_time_seconds": processing_stats.get("processing_time_seconds"),
            "validation_errors": validation_errors,
            "error_count": len(validation_errors),
        },
        # System information
        "system": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "torch_version": torch.__version__,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "cuda_available": torch.cuda.is_available(),
        },
    }

    return metadata


def run_batch_inference(
    lora_name: str,
    input_csv_path: str,
    output_dir: str,
    sequence_column: Optional[str] = None,
    lora_strength: float = 1.0,
    full_probabilities: bool = False,
    batch_size: int = 32,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run batch inference on CSV file and save results with metadata.

    Args:
        lora_name: Name of the LoRA model to use
        input_csv_path: Path to input CSV file
        output_dir: Directory to save output files
        sequence_column: Name of sequence column (auto-detected if None)
        lora_strength: LoRA strength parameter
        full_probabilities: Whether to return full probability distribution
        batch_size: Batch size for processing
        verbose: Whether to show detailed output

    Returns:
        Dict containing processing results and metadata

    Raises:
        FileNotFoundError: If input file or LoRA model doesn't exist
        ValueError: If CSV format is invalid or no valid sequences found
        RuntimeError: If inference fails
    """
    start_time = datetime.now()

    # Validate input file
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load and validate CSV data
    logger.info(f"Loading CSV file: {input_csv_path}")
    df = pd.read_csv(input_csv_path)

    # Auto-detect sequence column if not specified
    if sequence_column is None:
        sequence_column = auto_detect_sequence_column(df)

    # Validate and clean data
    df_cleaned, validation_errors = validate_csv_data(df, sequence_column)

    # Load model
    logger.info(f"Loading LoRA model: {lora_name}")
    model, tokenizer, base_model_name = load_lora_model(lora_name, lora_strength)

    # Prepare sequences for batch processing
    sequences = df_cleaned[sequence_column].tolist()

    # Process in batches
    predictions = []
    confidences = []

    logger.info(f"Processing {len(sequences)} sequences in batches of {batch_size}")

    for i in range(0, len(sequences), batch_size):
        batch_sequences = sequences[i : i + batch_size]
        batch_start = i + 1
        batch_end = min(i + batch_size, len(sequences))

        if verbose:
            logger.info(
                f"Processing batch {batch_start}-{batch_end} of {len(sequences)}"
            )

        # Tokenize batch
        inputs = tokenizer(
            batch_sequences,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True,
        )

        # Move inputs to device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

            # Process each prediction in the batch
            for j in range(len(batch_sequences)):
                batch_logits = logits[j : j + 1]
                prediction = process_model_outputs(batch_logits, full_probabilities)
                confidence = calculate_confidence(prediction)

                predictions.append(prediction)
                confidences.append(confidence)

    # Create output DataFrame
    df_output = df_cleaned.copy()

    # Add prediction columns
    if full_probabilities:
        # For full probabilities, create separate columns for each class
        if predictions and isinstance(predictions[0], list):
            num_classes = len(predictions[0])
            for i in range(num_classes):
                df_output[f"prediction_class_{i}"] = [
                    pred[i] for pred in predictions if isinstance(pred, list)
                ]
        else:
            df_output["prediction"] = predictions
    else:
        df_output["prediction"] = predictions

    df_output["confidence"] = confidences

    # Save output CSV
    output_csv_path = os.path.join(output_dir, "predictions.csv")
    df_output.to_csv(output_csv_path, index=False)
    logger.info(f"Saved predictions to: {output_csv_path}")

    # Calculate processing statistics
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    processing_stats = {
        "total_rows": len(df),
        "valid_rows": len(df_cleaned),
        "invalid_rows": len(df) - len(df_cleaned),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "processing_time_seconds": processing_time,
    }

    # Generate and save metadata
    metadata = generate_metadata(
        lora_name=lora_name,
        input_csv_path=input_csv_path,
        output_dir=output_dir,
        sequence_column=sequence_column,
        lora_strength=lora_strength,
        full_probabilities=full_probabilities,
        batch_size=batch_size,
        validation_errors=validation_errors,
        processing_stats=processing_stats,
    )

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to: {metadata_path}")

    # Print summary
    logger.info("=" * 60)
    logger.info("BATCH PREDICTION COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Input file: {input_csv_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Total sequences: {len(df)}")
    logger.info(f"Valid sequences: {len(df_cleaned)}")
    logger.info(f"Invalid sequences: {len(validation_errors)}")
    logger.info(f"Processing time: {processing_time:.2f} seconds")
    logger.info(
        f"Average time per sequence: {processing_time/len(df_cleaned):.4f} seconds"
    )

    if validation_errors:
        logger.warning(f"Validation errors: {len(validation_errors)}")
        for error in validation_errors[:5]:  # Show first 5 errors
            logger.warning(f"  - {error}")
        if len(validation_errors) > 5:
            logger.warning(f"  ... and {len(validation_errors) - 5} more errors")

    return {
        "success": True,
        "output_csv": output_csv_path,
        "metadata_file": metadata_path,
        "processing_stats": processing_stats,
        "validation_errors": validation_errors,
        "metadata": metadata,
    }
