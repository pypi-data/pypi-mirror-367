"""
ESM-2 inference module for Vaultide.

This module provides functionality to run inference using trained LoRA adapters
with configurable strength parameters.
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Union

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
from vaultide.config import get_lora_base_path

logger = logging.getLogger("vaultide")

# Valid amino acids for protein sequences
VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")


def validate_sequence(sequence: str) -> bool:
    """
    Validate that a sequence contains only valid amino acids.

    Args:
        sequence: Protein sequence to validate

    Returns:
        bool: True if sequence is valid
    """
    return all(c in VALID_AMINO_ACIDS for c in sequence.upper())


def load_lora_config(lora_path: str) -> Dict[str, Any]:
    """
    Load LoRA configuration from adapter_config.json.

    Args:
        lora_path: Path to the LoRA model directory

    Returns:
        Dict containing LoRA configuration

    Raises:
        FileNotFoundError: If LoRA config file doesn't exist
        ValueError: If base model name is missing from config
    """
    adapter_config_path = os.path.join(lora_path, "adapter_config.json")
    if not os.path.exists(adapter_config_path):
        raise FileNotFoundError(f"LoRA config not found: {adapter_config_path}")

    with open(adapter_config_path, "r") as f:
        adapter_config = json.load(f)

    base_model_name = adapter_config.get("base_model_name_or_path")
    if not base_model_name:
        raise ValueError("Base model name not found in LoRA config")

    return adapter_config


def apply_lora_strength(model: PeftModel, lora_strength: float) -> None:
    """
    Apply LoRA strength scaling to the model.

    Args:
        model: The PeftModel to modify
        lora_strength: Strength multiplier (0.0 to 2.0)
    """
    if lora_strength == 1.0:
        return  # No scaling needed

    logger.info(f"Applying LoRA strength: {lora_strength}")

    for name, module in model.named_modules():
        if hasattr(module, "lora_A") and hasattr(module, "lora_B"):
            if hasattr(module, "scaling"):
                orig_scaling = module.scaling
                try:
                    # If it's a float, just set it
                    if isinstance(orig_scaling, float):
                        module.scaling = lora_strength
                    # If it's a tensor, multiply by lora_strength
                    elif hasattr(orig_scaling, "mul"):
                        module.scaling = orig_scaling * lora_strength
                    # If it's a list or tuple, multiply each element
                    elif isinstance(orig_scaling, (list, tuple)):
                        module.scaling = type(orig_scaling)(
                            x * lora_strength for x in orig_scaling
                        )
                    # If it's a dict, try to scale the 'alpha' or 'weight' values
                    elif isinstance(orig_scaling, dict):
                        new_scaling = orig_scaling.copy()
                        # Scale common keys that might contain scaling values
                        for key in ["alpha", "weight", "scale"]:
                            if key in new_scaling and isinstance(
                                new_scaling[key], (int, float)
                            ):
                                new_scaling[key] = new_scaling[key] * lora_strength
                        module.scaling = new_scaling
                    else:
                        logger.warning(
                            f"Unknown scaling type for module {name}: {type(orig_scaling)}"
                        )
                except Exception as e:
                    logger.error(f"Failed to set scaling for module {name}: {e}")


def load_lora_model(
    lora_name: str, lora_strength: float = 1.0
) -> Tuple[PeftModel, AutoTokenizer, str]:
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
    lora_path = os.path.join(get_lora_base_path("esm2"), lora_name)

    if not os.path.exists(lora_path):
        raise FileNotFoundError(f"LoRA model not found: {lora_path}")

    # Load LoRA configuration
    adapter_config = load_lora_config(lora_path)
    base_model_name = adapter_config["base_model_name_or_path"]

    logger.info(f"Loading base model: {base_model_name}")
    logger.info(f"Loading LoRA adapter: {lora_name}")
    logger.info(f"LoRA strength: {lora_strength}")

    # Load tokenizer and base model
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )

    # Load LoRA adapter
    model = PeftModel.from_pretrained(model, lora_path)

    # Apply LoRA strength scaling
    apply_lora_strength(model, lora_strength)

    model.eval()

    return model, tokenizer, base_model_name


def process_model_outputs(
    logits: torch.Tensor, full_probabilities: bool = False
) -> Union[float, list]:
    """
    Process model outputs to get predictions.

    Args:
        logits: Raw model logits
        full_probabilities: Whether to return full probability distribution for binary

    Returns:
        Prediction as float (single probability) or list (distribution)
    """
    if logits.shape[-1] == 1:
        # Single output (sigmoid) - binary classification
        return torch.sigmoid(logits).item()
    elif logits.shape[-1] == 2:
        # Binary classification with 2 outputs
        probabilities = torch.softmax(logits, dim=-1)
        if full_probabilities:
            # Return full probability distribution
            return probabilities[0].tolist()
        else:
            # Return positive class probability (class 1)
            return probabilities[0][1].item()
    else:
        # Multi-class classification - always return full distribution
        probabilities = torch.softmax(logits, dim=-1)
        return probabilities[0].tolist()


def calculate_confidence(prediction: Union[float, list]) -> Optional[float]:
    """
    Calculate confidence score from prediction.

    Args:
        prediction: Model prediction (float or list)

    Returns:
        Confidence score or None if calculation fails
    """
    try:
        if isinstance(prediction, (int, float)):
            # Single probability (binary classification)
            return max(prediction, 1 - prediction)
        elif isinstance(prediction, list):
            # Probability distribution (multi-class or full binary)
            return max(prediction)
        else:
            return None
    except Exception as e:
        logger.warning(f"Failed to calculate confidence: {e}")
        return None


def run_inference(
    lora_name: str,
    sequence: str,
    lora_strength: float = 1.0,
    verbose: bool = False,
    full_probabilities: bool = False,
) -> Dict[str, Any]:
    """
    Run inference on a protein sequence using a trained LoRA model.

    Args:
        lora_name: Name of the LoRA model to use
        sequence: Protein sequence to predict on
        lora_strength: Strength of the LoRA adapter (0.0 to 2.0)
        verbose: Whether to include additional information in output
        full_probabilities: If True, return full probability distribution for binary classification

    Returns:
        Dict containing prediction results with keys:
        - prediction: Model prediction (float or list)
        - confidence: Confidence score (float or None)
        - base_model: Name of the base model
        - timestamp: ISO timestamp of inference

    Raises:
        ValueError: If sequence is invalid
        FileNotFoundError: If LoRA model doesn't exist
        RuntimeError: If inference fails
    """
    # Validate input sequence
    if not validate_sequence(sequence):
        raise ValueError(
            "Invalid protein sequence. Only standard amino acids (ACDEFGHIKLMNPQRSTVWY) are allowed."
        )

    try:
        # Load model
        model, tokenizer, base_model_name = load_lora_model(lora_name, lora_strength)

        # Tokenize sequence
        inputs = tokenizer(
            sequence,
            return_tensors="pt",
            truncation=True,
            max_length=1024,  # Adjust based on your model's max length
            padding=True,
        )

        # Move inputs to device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            prediction = process_model_outputs(logits, full_probabilities)

        # Calculate confidence
        confidence = calculate_confidence(prediction)

        result = {
            "prediction": prediction,
            "confidence": confidence,
            "base_model": base_model_name,
            "timestamp": datetime.now().isoformat(),
        }

        if verbose:
            logger.info(f"Prediction: {prediction}")
            logger.info(f"Confidence: {confidence}")

        return result

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise RuntimeError(f"Inference failed: {e}") from e
