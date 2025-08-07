"""
Configuration module for Vaultide.

This module centralizes all path configurations and constants used throughout the project.
"""

import os


# Base directory configuration
DEFAULT_VAULTIDE_HOME = os.path.expanduser("~/.vaultide")
DEFAULT_LORA_BASE = os.path.join(DEFAULT_VAULTIDE_HOME, "loras")
DEFAULT_DATA_DIR = os.path.join(DEFAULT_VAULTIDE_HOME, "data")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_VAULTIDE_HOME, "config", "config.yaml")


def get_lora_base_path(model_type: str = "esm2") -> str:
    """
    Get the LoRA base path for a specific model type.

    Args:
        model_type: The model type (e.g., "esm2")

    Returns:
        The LoRA base path for the specified model type
    """
    return os.path.join(DEFAULT_LORA_BASE, model_type)


def get_vaultide_home() -> str:
    """
    Get the Vaultide home directory.

    Returns:
        The Vaultide home directory path
    """
    return DEFAULT_VAULTIDE_HOME


def get_data_dir() -> str:
    """
    Get the default data directory.

    Returns:
        The default data directory path
    """
    return DEFAULT_DATA_DIR


def get_config_path() -> str:
    """
    Get the default config file path.

    Returns:
        The default config file path
    """
    return DEFAULT_CONFIG_PATH


def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs(DEFAULT_VAULTIDE_HOME, exist_ok=True)
    os.makedirs(DEFAULT_LORA_BASE, exist_ok=True)
    os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DEFAULT_CONFIG_PATH), exist_ok=True)
