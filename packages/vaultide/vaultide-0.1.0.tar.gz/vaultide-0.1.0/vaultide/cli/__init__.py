"""
Vaultide CLI - Feature-agnostic command-line interface for training biomolecular model LoRAs.

This module provides a feature-agnostic CLI that allows different model types to define
their own required features and validation logic.
"""

from .main import main
from .cli import VaultideCLI
from .security import SecurityError, PathValidator, ModelValidator, SecureFileHandler
from .features import (
    FeatureValidator,
    Esm2FeatureValidator,
    FEATURE_VALIDATORS,
)
from vaultide.config import (
    get_vaultide_home,
    get_data_dir,
    get_config_path,
    get_lora_base_path,
)

# Default paths - re-export for backward compatibility
DEFAULT_VAULTIDE_HOME = get_vaultide_home()
DEFAULT_LORA_BASE = get_lora_base_path()  # This will be the esm2 path by default
DEFAULT_DATA_DIR = get_data_dir()
DEFAULT_CONFIG_PATH = get_config_path()

__all__ = [
    "main",
    "VaultideCLI",
    "SecurityError",
    "PathValidator",
    "ModelValidator",
    "SecureFileHandler",
    "FeatureValidator",
    "Esm2FeatureValidator",
    "FEATURE_VALIDATORS",
    "DEFAULT_VAULTIDE_HOME",
    "DEFAULT_LORA_BASE",
    "DEFAULT_DATA_DIR",
    "DEFAULT_CONFIG_PATH",
]
