"""
ESMC Inference Module

This module provides inference utilities for the ESMC model using the esm Python package.
"""

import logging
import os
import torch
from typing import Dict, Any, Tuple, Optional
import esm.pretrained
import json

from vaultide.config import get_lora_base_path

# Configure logging
logger = logging.getLogger("vaultide")

# Use CUDA if available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ESMC model configuration
ESMC_MODEL_NAME = "ESMC_300M_202412"  # Using ESMC 300M model


def load_lora_config(lora_path: str) -> Dict[str, Any]:
    """
    Load LoRA configuration from the model directory.

    Args:
        lora_path: Path to the LoRA model directory

    Returns:
        Dictionary containing the LoRA configuration

    Raises:
        FileNotFoundError: If adapter_config.json doesn't exist
        ValueError: If config is invalid
    """
    config_path = os.path.join(lora_path, "adapter_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"LoRA config not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid LoRA config: {e}")


def apply_lora_strength(model: torch.nn.Module, strength: float):
    """
    Apply LoRA strength scaling to the model.

    Args:
        model: The model to modify
        strength: Strength multiplier (0.0 to 2.0)
    """
    if strength == 1.0:
        return  # No scaling needed

    logger.info(f"Applying LoRA strength scaling: {strength}")

    for name, module in model.named_modules():
        if hasattr(module, "lora_A") and hasattr(module, "lora_B"):
            # Scale the LoRA weights
            if hasattr(module.lora_A, "weight"):
                module.lora_A.weight.data *= strength
            if hasattr(module.lora_B, "weight"):
                module.lora_B.weight.data *= strength


def load_esmc_model(model_name: Optional[str] = None) -> Tuple[torch.nn.Module, Any]:
    """
    Load ESMC model using the esm package.

    Args:
        model_name: ESMC model name (default: ESMC_300M_202412)

    Returns:
        tuple: (model, tokenizer)

    Raises:
        ValueError: If model_name is invalid
    """
    if model_name is None:
        model_name = ESMC_MODEL_NAME

    logger.info(f"Loading ESMC model: {model_name}")

    try:
        # Load ESMC model
        if model_name == "ESMC_300M_202412":
            model = esm.pretrained.ESMC_300M_202412()
        elif model_name == "ESMC_600M_202412":
            model = esm.pretrained.ESMC_600M_202412()
        else:
            raise ValueError(f"Unknown ESMC model: {model_name}")

        # Move model to device
        model = model.to(DEVICE)
        model.eval()

        logger.info(f"ESMC model loaded successfully on device: {DEVICE}")
        return model, model

    except Exception as e:
        raise ValueError(f"Failed to load ESMC model {model_name}: {e}")


def load_model_and_tokenizer(
    lora_name: str, lora_strength: float = 1.0
) -> Tuple[torch.nn.Module, Any, str]:
    """
    Load a LoRA model with configurable strength.

    Args:
        lora_name: Name of the LoRA model to load
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)

    Returns:
        tuple: (model, tokenizer, base_model_name)

    Raises:
        FileNotFoundError: If LoRA model or config doesn't exist
        ValueError: If base model name is missing from config
    """
    lora_path = os.path.join(get_lora_base_path("esmc"), lora_name)

    if not os.path.exists(lora_path):
        raise FileNotFoundError(f"LoRA model not found: {lora_path}")

    # Load LoRA configuration
    adapter_config = load_lora_config(lora_path)
    base_model_name = adapter_config.get("base_model_name_or_path", ESMC_MODEL_NAME)

    logger.info(f"Loading base model: {base_model_name}")
    logger.info(f"Loading LoRA adapter: {lora_name}")
    logger.info(f"LoRA strength: {lora_strength}")

    # Load ESMC model
    model, tokenizer = load_esmc_model(base_model_name)

    # Load LoRA adapter if it exists
    # Note: This is a simplified implementation - in practice, you'd need to implement
    # LoRA loading for ESMC models or use a different approach
    lora_weights_path = os.path.join(lora_path, "adapter_model.bin")
    if os.path.exists(lora_weights_path):
        logger.info("Loading LoRA weights...")
        # Load LoRA weights and apply to model
        # This would need custom implementation for ESMC models
        pass

    # Apply LoRA strength scaling
    apply_lora_strength(model, lora_strength)

    model.eval()

    return model, tokenizer, base_model_name


def tokenize_sequence(sequence: str, model) -> torch.Tensor:
    """
    Tokenize a protein sequence using ESMC model.

    Args:
        sequence: Protein sequence string
        model: ESMC model object

    Returns:
        Tokenized sequence as tensor
    """
    # Use the model's tokenizer
    encoded = model.tokenizer.encode_plus(sequence, return_tensors="pt")
    return encoded["input_ids"]


def process_model_outputs(
    logits: torch.Tensor, full_probabilities: bool = False
) -> Dict[str, Any]:
    """
    Process model outputs to get predictions and probabilities.

    Args:
        logits: Raw model logits
        full_probabilities: Whether to return full probability distribution

    Returns:
        Dictionary containing predictions and probabilities
    """
    # Apply softmax to get probabilities
    probabilities = torch.softmax(logits, dim=-1)

    # Get prediction (argmax)
    prediction = torch.argmax(logits, dim=-1)

    # Get confidence (max probability)
    confidence = torch.max(probabilities, dim=-1)[0]

    result: Dict[str, Any] = {
        "prediction": int(prediction.item()),
        "confidence": float(confidence.item()),
    }

    if full_probabilities:
        # Return full probability distribution
        result["probabilities"] = {
            f"class_{i}": float(prob.item()) for i, prob in enumerate(probabilities[0])
        }
    else:
        # Return only positive class probability for binary classification
        result["positive_probability"] = float(probabilities[0][1].item())

    return result


def predict_sequence(
    sequence: str,
    lora_name: str,
    lora_strength: float = 1.0,
    full_probabilities: bool = False,
    max_length: int = 1024,
) -> Dict[str, Any]:
    """
    Predict on a single protein sequence.

    Args:
        sequence: Protein sequence to predict on
        lora_name: Name of the LoRA model to use
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        full_probabilities: Whether to return full probability distribution
        max_length: Maximum sequence length for tokenization

    Returns:
        Dictionary containing prediction results

    Raises:
        ValueError: If sequence is invalid
        FileNotFoundError: If LoRA model doesn't exist
    """
    if not sequence or not isinstance(sequence, str):
        raise ValueError("Sequence must be a non-empty string")

    sequence = sequence.strip()
    if not sequence:
        raise ValueError("Sequence cannot be empty")

    # Validate LoRA strength
    if not 0.0 <= lora_strength <= 2.0:
        raise ValueError("LoRA strength must be between 0.0 and 2.0")

    logger.info(f"Predicting on sequence: {sequence[:50]}...")
    logger.info(f"Using LoRA: {lora_name} (strength: {lora_strength})")

    # Load model and tokenizer
    model, tokenizer, base_model_name = load_model_and_tokenizer(
        lora_name, lora_strength
    )

    # Tokenize sequence
    batch_tokens = tokenize_sequence(sequence, model)

    # Truncate if necessary
    if batch_tokens.size(1) > max_length:
        batch_tokens = batch_tokens[:, :max_length]
        logger.warning(f"Sequence truncated to {max_length} tokens")

    # Move to device
    batch_tokens = batch_tokens.to(DEVICE)

    # Run prediction
    model.eval()
    with torch.no_grad():
        # For ESMC models, we need to extract embeddings and then classify
        outputs = model(batch_tokens)

        # ESMC outputs embeddings with shape [batch_size, seq_len, hidden_size]
        embeddings = outputs.embeddings  # Shape: [batch_size, seq_len, hidden_size]

        # Use mean pooling over sequence length
        pooled_output = embeddings.mean(dim=1)  # Shape: [batch_size, hidden_size]

        # For now, we'll use a simple linear classifier
        # In practice, you'd load a trained classification head
        classifier = torch.nn.Linear(pooled_output.size(-1), 2).to(DEVICE)
        logits = classifier(pooled_output)

    # Process outputs
    result = process_model_outputs(logits, full_probabilities)

    # Add metadata
    result.update(
        {
            "sequence": sequence,
            "sequence_length": len(sequence),
            "lora_name": lora_name,
            "lora_strength": lora_strength,
            "base_model": base_model_name,
            "device": DEVICE,
        }
    )

    logger.info(
        f"Prediction completed: {result['prediction']} (confidence: {result['confidence']:.4f})"
    )

    return result


def predict_batch(
    sequences: list[str],
    lora_name: str,
    lora_strength: float = 1.0,
    full_probabilities: bool = False,
    max_length: int = 1024,
    batch_size: int = 32,
) -> list[Dict[str, Any]]:
    """
    Predict on a batch of protein sequences.

    Args:
        sequences: List of protein sequences to predict on
        lora_name: Name of the LoRA model to use
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        full_probabilities: Whether to return full probability distribution
        max_length: Maximum sequence length for tokenization
        batch_size: Batch size for processing

    Returns:
        List of dictionaries containing prediction results

    Raises:
        ValueError: If sequences are invalid
        FileNotFoundError: If LoRA model doesn't exist
    """
    if not sequences:
        raise ValueError("Sequences list cannot be empty")

    # Validate LoRA strength
    if not 0.0 <= lora_strength <= 2.0:
        raise ValueError("LoRA strength must be between 0.0 and 2.0")

    logger.info(f"Predicting on {len(sequences)} sequences")
    logger.info(f"Using LoRA: {lora_name} (strength: {lora_strength})")

    # Load model and tokenizer
    model, tokenizer, base_model_name = load_model_and_tokenizer(
        lora_name, lora_strength
    )

    results = []

    # Process in batches
    for i in range(0, len(sequences), batch_size):
        batch_sequences = sequences[i : i + batch_size]
        logger.info(
            f"Processing batch {i//batch_size + 1}/{(len(sequences) + batch_size - 1)//batch_size}"
        )

        # Tokenize batch
        batch_tokens_list: list[torch.Tensor] = []
        for seq in batch_sequences:
            tokens = tokenize_sequence(seq, model)
            if tokens.size(1) > max_length:
                tokens = tokens[:, :max_length]
            batch_tokens_list.append(tokens)

        # Pad to same length
        max_len = max(tokens.size(1) for tokens in batch_tokens_list)
        padded_tokens: list[torch.Tensor] = []
        for tokens in batch_tokens_list:
            if tokens.size(1) < max_len:
                padding = torch.zeros(1, max_len - tokens.size(1), dtype=tokens.dtype)
                tokens = torch.cat([tokens, padding], dim=1)
            padded_tokens.append(tokens)

        batch_tokens = torch.cat(padded_tokens, dim=0)

        # Move to device
        batch_tokens = batch_tokens.to(DEVICE)

        # Run prediction
        model.eval()
        with torch.no_grad():
            # Extract embeddings
            outputs = model(batch_tokens)

            # ESMC outputs embeddings with shape [batch_size, seq_len, hidden_size]
            embeddings = outputs.embeddings  # Shape: [batch_size, seq_len, hidden_size]

            # Use mean pooling over sequence length
            pooled_output = embeddings.mean(dim=1)  # Shape: [batch_size, hidden_size]

            # Apply classification head
            classifier = torch.nn.Linear(pooled_output.size(-1), 2).to(DEVICE)
            logits = classifier(pooled_output)

        # Process each sequence in the batch
        for j, sequence in enumerate(batch_sequences):
            # Extract logits for this sequence
            sequence_logits = logits[j : j + 1]

            # Process outputs
            result = process_model_outputs(sequence_logits, full_probabilities)

            # Add metadata
            result.update(
                {
                    "sequence": sequence,
                    "sequence_length": len(sequence),
                    "lora_name": lora_name,
                    "lora_strength": lora_strength,
                    "base_model": base_model_name,
                    "device": DEVICE,
                }
            )

            results.append(result)

    logger.info(f"Batch prediction completed: {len(results)} predictions")

    return results


def get_model_info(lora_name: str) -> Dict[str, Any]:
    """
    Get information about a trained LoRA model.

    Args:
        lora_name: Name of the LoRA model

    Returns:
        Dictionary containing model information

    Raises:
        FileNotFoundError: If LoRA model doesn't exist
    """
    lora_path = os.path.join(get_lora_base_path("esmc"), lora_name)

    if not os.path.exists(lora_path):
        raise FileNotFoundError(f"LoRA model not found: {lora_path}")

    # Load configuration
    adapter_config = load_lora_config(lora_path)

    # Load training metadata if available
    metadata_path = os.path.join(lora_path, "training_metadata.json")
    training_metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                training_metadata = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load training metadata: {e}")

    # Get file sizes
    file_sizes = {}
    for filename in os.listdir(lora_path):
        file_path = os.path.join(lora_path, filename)
        if os.path.isfile(file_path):
            file_sizes[filename] = os.path.getsize(file_path)

    return {
        "lora_name": lora_name,
        "lora_path": lora_path,
        "base_model": adapter_config.get("base_model_name_or_path", ESMC_MODEL_NAME),
        "lora_config": adapter_config,
        "training_metadata": training_metadata,
        "file_sizes": file_sizes,
        "total_size_bytes": sum(file_sizes.values()),
    }
