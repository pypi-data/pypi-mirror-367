"""
Security utilities for Vaultide CLI.

This module provides security-related classes and utilities for path validation,
model validation, and secure file operations.
"""

import json
import os
import re
import tempfile
from typing import Any, Dict, Optional


class SecurityError(Exception):
    """Custom exception for security-related errors."""

    pass


class PathValidator:
    """Utility class for secure path validation and sanitization."""

    # Allowed characters for file/directory names (alphanumeric, hyphens, underscores, dots)
    ALLOWED_CHARS = re.compile(r"^[a-zA-Z0-9._-]+$")

    # Dangerous path patterns that could lead to path traversal
    DANGEROUS_PATTERNS = [
        "..",  # Directory traversal
        "//",  # Multiple slashes
        "\\",  # Windows backslash
        ":",  # Drive letter (Windows)
    ]

    @staticmethod
    def is_safe_path(path: str, base_dir: Optional[str] = None) -> bool:
        """
        Validate that a path is safe and doesn't contain path traversal attempts.

        Args:
            path: Path to validate
            base_dir: Base directory to restrict paths to (optional)

        Returns:
            bool: True if path is safe

        Raises:
            SecurityError: If path contains dangerous patterns
        """
        if not path:
            raise SecurityError("Path cannot be empty")

        # Check for dangerous patterns in the original path
        for pattern in PathValidator.DANGEROUS_PATTERNS:
            if pattern in path:
                raise SecurityError(f"Path contains dangerous pattern: {pattern}")

        # Normalize the path
        normalized_path = os.path.normpath(path)

        # Check for absolute paths if base_dir is specified
        if base_dir and os.path.isabs(normalized_path):
            raise SecurityError(
                "Absolute paths are not allowed when base directory is specified"
            )

        # If base_dir is specified, ensure the path is within the base directory
        if base_dir:
            try:
                full_path = os.path.abspath(os.path.join(base_dir, normalized_path))
                base_abs = os.path.abspath(base_dir)
                if not full_path.startswith(base_abs):
                    raise SecurityError(
                        f"Path {normalized_path} is outside allowed directory {base_dir}"
                    )
            except (OSError, ValueError) as e:
                raise SecurityError(f"Invalid path: {e}")

        # Additional validation for absolute paths (even without base_dir)
        if os.path.isabs(normalized_path):
            # Allow temporary directories for testing
            temp_dir = tempfile.gettempdir()
            if normalized_path.startswith(temp_dir):
                return True

            # Check for system directories
            system_dirs = ["/etc", "/usr", "/bin", "/sbin", "/var", "/home"]
            for sys_dir in system_dirs:
                if normalized_path.startswith(sys_dir):
                    raise SecurityError(
                        f"Access to system directory not allowed: {sys_dir}"
                    )

        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to remove dangerous characters.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        if not filename:
            raise SecurityError("Filename cannot be empty")

        # Remove or replace dangerous characters
        sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Ensure it's not empty after sanitization
        if not sanitized:
            raise SecurityError("Filename becomes empty after sanitization")

        # Prevent hidden files and handle multiple dots
        if sanitized.startswith("."):
            sanitized = "_" + sanitized

        # Remove multiple consecutive dots
        sanitized = re.sub(r"\.+", ".", sanitized)

        return sanitized

    @staticmethod
    def validate_model_name(model_name: str) -> str:
        """
        Validate and sanitize a model name.

        Args:
            model_name: Model name to validate

        Returns:
            str: Validated model name

        Raises:
            SecurityError: If model name is invalid
        """
        if not model_name:
            raise SecurityError("Model name cannot be empty")

        # Check length
        if len(model_name) > 100:
            raise SecurityError("Model name too long (max 100 characters)")

        # Check for dangerous patterns
        for pattern in PathValidator.DANGEROUS_PATTERNS:
            if pattern in model_name:
                raise SecurityError(f"Model name contains dangerous pattern: {pattern}")

        # Check for invalid characters before sanitization
        if not re.match(r"^[a-zA-Z0-9._-]+$", model_name):
            raise SecurityError("Model name contains invalid characters")

        # Sanitize the name
        sanitized = PathValidator.sanitize_filename(model_name)

        return sanitized


class ModelValidator:
    """Utility class for validating model files and configurations."""

    # Required files for a valid LoRA model
    REQUIRED_FILES = {
        "adapter_config.json",
    }

    # Required model weight files (either .bin or .safetensors)
    REQUIRED_WEIGHT_FILES = {
        "adapter_model.bin",
        "adapter_model.safetensors",
    }

    # Optional files that may be present
    OPTIONAL_FILES = {
        "training_args.json",
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
    }

    # Maximum file sizes (in bytes) to prevent DoS attacks
    MAX_FILE_SIZES = {
        "adapter_config.json": 1024 * 1024,  # 1MB
        "adapter_model.bin": 1024 * 1024 * 1024,  # 1GB
        "training_args.json": 1024 * 1024,  # 1MB
        "config.json": 1024 * 1024,  # 1MB
    }

    @staticmethod
    def validate_model_directory(model_path: str) -> Dict[str, Any]:
        """
        Validate a model directory and its contents.

        Args:
            model_path: Path to the model directory

        Returns:
            Dict containing validation results

        Raises:
            SecurityError: If model directory is invalid or unsafe
        """
        # Validate the path itself
        PathValidator.is_safe_path(model_path)

        if not os.path.exists(model_path):
            raise SecurityError(f"Model directory does not exist: {model_path}")

        if not os.path.isdir(model_path):
            raise SecurityError(f"Model path is not a directory: {model_path}")

        # Check for required files
        files_present = set()
        file_sizes = {}

        try:
            for item in os.listdir(model_path):
                item_path = os.path.join(model_path, item)

                # Skip subdirectories
                if os.path.isdir(item_path):
                    continue

                # Validate filename
                PathValidator.sanitize_filename(item)
                files_present.add(item)

                # Check file size
                try:
                    file_size = os.path.getsize(item_path)
                    file_sizes[item] = file_size

                    # Check against maximum size
                    if item in ModelValidator.MAX_FILE_SIZES:
                        max_size = ModelValidator.MAX_FILE_SIZES[item]
                        if file_size > max_size:
                            raise SecurityError(
                                f"File {item} is too large ({file_size} bytes, max {max_size})"
                            )
                except OSError as e:
                    raise SecurityError(f"Cannot access file {item}: {e}")

        except OSError as e:
            raise SecurityError(f"Cannot read model directory {model_path}: {e}")

        # Check for required files
        missing_files = ModelValidator.REQUIRED_FILES - files_present
        if missing_files:
            raise SecurityError(f"Missing required files: {missing_files}")

        # Check for required weight files (either .bin or .safetensors)
        weight_files_present = files_present & ModelValidator.REQUIRED_WEIGHT_FILES
        if not weight_files_present:
            raise SecurityError(
                f"Missing required weight files. Need one of: {ModelValidator.REQUIRED_WEIGHT_FILES}"
            )

        # Validate adapter_config.json specifically
        config_path = os.path.join(model_path, "adapter_config.json")
        ModelValidator.validate_config_file(config_path)

        return {
            "valid": True,
            "files_present": files_present,
            "file_sizes": file_sizes,
            "missing_files": list(missing_files),
        }

    @staticmethod
    def validate_config_file(config_path: str) -> Dict[str, Any]:
        """
        Validate a model configuration file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dict containing configuration data

        Raises:
            SecurityError: If configuration file is invalid or unsafe
        """
        if not os.path.exists(config_path):
            raise SecurityError(f"Configuration file does not exist: {config_path}")

        # Check file size
        try:
            file_size = os.path.getsize(config_path)
            if file_size > ModelValidator.MAX_FILE_SIZES.get(
                "adapter_config.json", 1024 * 1024
            ):
                raise SecurityError(
                    f"Configuration file is too large ({file_size} bytes)"
                )
        except OSError as e:
            raise SecurityError(f"Cannot access configuration file: {e}")

        # Read and validate JSON
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise SecurityError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise SecurityError(f"Error reading configuration file: {e}")

        # Validate required fields
        required_fields = ["base_model_name_or_path"]
        for field in required_fields:
            if field not in config:
                raise SecurityError(f"Missing required field in configuration: {field}")

        # Check for either model_type or peft_type (for compatibility)
        if "model_type" not in config and "peft_type" not in config:
            raise SecurityError(
                "Missing required field in configuration: model_type or peft_type"
            )

        # Validate base model name
        base_model = config.get("base_model_name_or_path", "")
        if not base_model:
            raise SecurityError("Base model name cannot be empty")

        # Check for dangerous patterns in base model name
        for pattern in PathValidator.DANGEROUS_PATTERNS:
            if pattern in base_model:
                raise SecurityError(
                    f"Base model name contains dangerous pattern: {pattern}"
                )

        return config


class SecureFileHandler:
    """Utility class for secure file operations."""

    @staticmethod
    def safe_open(
        file_path: str, mode: str = "r", base_dir: Optional[str] = None
    ) -> Any:
        """
        Safely open a file with path validation.

        Args:
            file_path: Path to the file
            mode: File open mode
            base_dir: Base directory to restrict paths to (optional)

        Returns:
            File object

        Raises:
            SecurityError: If file path is unsafe
        """
        # Validate the path
        PathValidator.is_safe_path(file_path, base_dir)

        # Additional validation for write modes
        if "w" in mode or "a" in mode:
            # Allow temporary directories for testing
            abs_path = os.path.abspath(file_path)
            temp_dir = tempfile.gettempdir()
            if abs_path.startswith(temp_dir):
                pass  # Allow temporary directories
            else:
                # Ensure we're not writing to system directories
                system_dirs = [
                    "/etc",
                    "/usr",
                    "/bin",
                    "/sbin",
                    "/var",
                    "/home",
                ]
                for sys_dir in system_dirs:
                    if abs_path.startswith(sys_dir):
                        raise SecurityError(
                            f"Cannot write to system directory: {sys_dir}"
                        )

        try:
            return open(file_path, mode)
        except Exception as e:
            raise SecurityError(f"Error opening file {file_path}: {e}")

    @staticmethod
    def safe_read_json(
        file_path: str, base_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Safely read a JSON file with path validation.

        Args:
            file_path: Path to the JSON file
            base_dir: Base directory to restrict paths to (optional)

        Returns:
            Dict containing JSON data

        Raises:
            SecurityError: If file path is unsafe or JSON is invalid
        """
        with SecureFileHandler.safe_open(file_path, "r", base_dir) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise SecurityError(f"Invalid JSON in file {file_path}: {e}")

    @staticmethod
    def safe_write_json(
        file_path: str, data: Dict[str, Any], base_dir: Optional[str] = None
    ) -> None:
        """
        Safely write JSON data to a file with path validation.

        Args:
            file_path: Path to write the JSON file
            data: Data to write
            base_dir: Base directory to restrict paths to (optional)

        Raises:
            SecurityError: If file path is unsafe
        """
        with SecureFileHandler.safe_open(file_path, "w", base_dir) as f:
            try:
                json.dump(data, f, indent=2)
            except Exception as e:
                raise SecurityError(f"Error writing JSON to file {file_path}: {e}")
