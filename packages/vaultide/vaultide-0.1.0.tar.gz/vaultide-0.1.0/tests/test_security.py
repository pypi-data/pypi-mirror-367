#!/usr/bin/env python3
"""
Security tests for Vaultide CLI.

These tests verify that the security features work correctly and catch
potential security vulnerabilities.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the CLI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vaultide.cli import (
    SecurityError, 
    PathValidator, 
    ModelValidator, 
    SecureFileHandler,
    VaultideCLI
)


class TestPathValidator:
    """Test cases for PathValidator security features."""

    def test_safe_path_validation(self):
        """Test that safe paths are accepted."""
        safe_paths = [
            "data/train.csv",
            "models/model1",
            "config.yaml",
            "test_file.txt",
            "model_123",
        ]
        
        for path in safe_paths:
            assert PathValidator.is_safe_path(path) is True

    def test_dangerous_path_detection(self):
        """Test detection of dangerous path patterns."""
        # Test directory traversal
        with pytest.raises(SecurityError):
            PathValidator.is_safe_path('path/../etc/passwd')
        
        # Test multiple slashes
        with pytest.raises(SecurityError):
            PathValidator.is_safe_path('path//etc/passwd')
        
        # Test Windows backslash
        with pytest.raises(SecurityError):
            PathValidator.is_safe_path('path\\etc\\passwd')
        
        # Test drive letter (Windows)
        with pytest.raises(SecurityError):
            PathValidator.is_safe_path('C:path\\etc\\passwd')

    def test_base_directory_restriction(self):
        """Test that paths are restricted to base directory."""
        base_dir = "/tmp/test"
        
        # Safe relative paths
        safe_paths = ["file.txt", "subdir/file.csv", "model/config.json"]
        for path in safe_paths:
            assert PathValidator.is_safe_path(path, base_dir) is True
        
        # Dangerous absolute paths
        dangerous_paths = ["/etc/passwd", "/var/log/syslog"]
        for path in dangerous_paths:
            with pytest.raises(SecurityError):
                PathValidator.is_safe_path(path, base_dir)

    def test_filename_sanitization(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file@#$%^&*.txt", "file_______.txt"),
            ("..hidden_file", "_.hidden_file"),
            ("file/with/slashes.txt", "file_with_slashes.txt"),
        ]
        
        for input_name, expected_output in test_cases:
            result = PathValidator.sanitize_filename(input_name)
            assert result == expected_output

    def test_model_name_validation(self):
        """Test model name validation."""
        valid_names = [
            "my_model",
            "model_123",
            "test-model",
            "model.with.dots",
        ]
        
        for name in valid_names:
            result = PathValidator.validate_model_name(name)
            assert result == name
        
        invalid_names = [
            "",  # Empty
            "a" * 101,  # Too long
            "model/with/slash",
            "model\\with\\backslash",
            "model..with..dots",
            "model~with~tilde",
        ]
        
        for name in invalid_names:
            with pytest.raises(SecurityError):
                PathValidator.validate_model_name(name)


class TestModelValidator:
    """Test cases for ModelValidator security features."""

    def test_model_directory_validation(self, temp_dir):
        """Test model directory validation."""
        # Create a valid model directory
        model_dir = os.path.join(temp_dir, "valid_model")
        os.makedirs(model_dir)
        
        # Create required files
        config_content = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "model_type": "lora"
        }
        
        import json
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            json.dump(config_content, f)
        
        # Create a dummy model file
        with open(os.path.join(model_dir, "adapter_model.bin"), "w") as f:
            f.write("dummy model content")
        
        # Validate the directory
        result = ModelValidator.validate_model_directory(model_dir)
        assert result["valid"] is True
        assert "adapter_config.json" in result["files_present"]
        assert "adapter_model.bin" in result["files_present"]

    def test_missing_required_files(self, temp_dir):
        """Test validation fails when required files are missing."""
        model_dir = os.path.join(temp_dir, "invalid_model")
        os.makedirs(model_dir)
        
        # Only create config file, missing model file
        config_content = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "model_type": "lora"
        }
        
        import json
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            json.dump(config_content, f)
        
        with pytest.raises(SecurityError):
            ModelValidator.validate_model_directory(model_dir)

    def test_large_file_detection(self, temp_dir):
        """Test that large files are rejected."""
        model_dir = os.path.join(temp_dir, "large_file_model")
        os.makedirs(model_dir)
        
        # Create a large config file
        large_content = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            f.write(large_content)
        
        with open(os.path.join(model_dir, "adapter_model.bin"), "w") as f:
            f.write("dummy model content")
        
        with pytest.raises(SecurityError):
            ModelValidator.validate_model_directory(model_dir)

    def test_config_file_validation(self, temp_dir):
        """Test configuration file validation."""
        config_file = os.path.join(temp_dir, "adapter_config.json")
        
        # Valid config
        valid_config = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "model_type": "lora"
        }
        
        import json
        with open(config_file, "w") as f:
            json.dump(valid_config, f)
        
        result = ModelValidator.validate_config_file(config_file)
        assert result["base_model_name_or_path"] == "facebook/esm2_t33_650M_UR50D"
        
        # Invalid config - missing required field
        invalid_config = {"model_type": "lora"}
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)
        
        with pytest.raises(SecurityError):
            ModelValidator.validate_config_file(config_file)

    def test_dangerous_base_model_name(self, temp_dir):
        """Test that dangerous base model names are rejected."""
        config_file = os.path.join(temp_dir, "adapter_config.json")
        
        # Dangerous base model name
        dangerous_config = {
            "base_model_name_or_path": "../../../etc/passwd",
            "model_type": "lora"
        }
        
        import json
        with open(config_file, "w") as f:
            json.dump(dangerous_config, f)
        
        with pytest.raises(SecurityError):
            ModelValidator.validate_config_file(config_file)

    def test_safetensors_support(self, temp_dir):
        """Test that safetensors files are accepted."""
        # Create a valid model directory with safetensors
        model_dir = os.path.join(temp_dir, "safetensors_model")
        os.makedirs(model_dir)
        
        # Create required files
        config_content = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "peft_type": "LORA"  # Use peft_type instead of model_type
        }
        
        import json
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            json.dump(config_content, f)
        
        # Create a safetensors file instead of .bin
        with open(os.path.join(model_dir, "adapter_model.safetensors"), "w") as f:
            f.write("dummy safetensors content")
        
        # Validate the directory - should pass with safetensors
        result = ModelValidator.validate_model_directory(model_dir)
        assert result["valid"] is True
        assert "adapter_config.json" in result["files_present"]
        assert "adapter_model.safetensors" in result["files_present"]

    def test_weight_file_requirement(self, temp_dir):
        """Test that at least one weight file (.bin or .safetensors) is required."""
        model_dir = os.path.join(temp_dir, "no_weight_model")
        os.makedirs(model_dir)
        
        # Create config file but no weight files
        config_content = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "peft_type": "LORA"
        }
        
        import json
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            json.dump(config_content, f)
        
        # Should fail because no weight files are present
        with pytest.raises(SecurityError, match="Missing required weight files"):
            ModelValidator.validate_model_directory(model_dir)


class TestSecureFileHandler:
    """Test cases for SecureFileHandler security features."""

    def test_safe_file_operations(self, temp_dir):
        """Test safe file operations."""
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = "Hello, World!"
        
        # Safe write
        with SecureFileHandler.safe_open(test_file, "w") as f:
            f.write(test_content)
        
        # Safe read
        with SecureFileHandler.safe_open(test_file, "r") as f:
            content = f.read()
        
        assert content == test_content

    def test_dangerous_file_paths(self):
        """Test that dangerous file paths are rejected."""
        dangerous_paths = [
            "/etc/passwd",
            "../../../etc/shadow",
            "~/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
        ]
        
        for path in dangerous_paths:
            with pytest.raises(SecurityError):
                with SecureFileHandler.safe_open(path, "r"):
                    pass

    def test_safe_json_operations(self, temp_dir):
        """Test safe JSON operations."""
        json_file = os.path.join(temp_dir, "test.json")
        test_data = {"key": "value", "number": 42}
        
        # Safe write JSON
        SecureFileHandler.safe_write_json(json_file, test_data)
        
        # Safe read JSON
        result = SecureFileHandler.safe_read_json(json_file)
        assert result == test_data

    def test_invalid_json_handling(self, temp_dir):
        """Test handling of invalid JSON."""
        json_file = os.path.join(temp_dir, "invalid.json")
        
        # Write invalid JSON
        with open(json_file, "w") as f:
            f.write("{ invalid json }")
        
        with pytest.raises(SecurityError):
            SecureFileHandler.safe_read_json(json_file)


class TestCLISecurity:
    """Test cases for CLI security features."""

    def test_cli_initialization_security(self, temp_dir):
        """Test that CLI initialization uses secure paths."""
        with pytest.raises(SecurityError):
            # Try to use a dangerous config path
            cli = VaultideCLI("/etc/passwd")

    def test_data_path_validation(self):
        """Test that data paths are validated for security."""
        cli = VaultideCLI()
        
        # Test with dangerous path
        with pytest.raises(ValueError):
            cli.validate_dataset_features('esm2', ['path/../etc/passwd'], {})

    def test_model_name_validation_in_cli(self):
        """Test that model names are validated in CLI operations."""
        cli = VaultideCLI()
        
        # Valid model names
        valid_names = ["my_model", "model_123", "test-model"]
        for name in valid_names:
            try:
                PathValidator.validate_model_name(name)
            except SecurityError:
                pytest.fail(f"Valid model name {name} was rejected")
        
        # Invalid model names
        invalid_names = ["model/with/slash", "model..with..dots", ""]
        for name in invalid_names:
            with pytest.raises(SecurityError):
                PathValidator.validate_model_name(name)


class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_end_to_end_security(self, temp_dir):
        """Test end-to-end security in a realistic scenario."""
        # Create a valid model directory
        model_dir = os.path.join(temp_dir, "test_model")
        os.makedirs(model_dir)
        
        # Create valid model files
        config_content = {
            "base_model_name_or_path": "facebook/esm2_t33_650M_UR50D",
            "model_type": "lora"
        }
        
        import json
        with open(os.path.join(model_dir, "adapter_config.json"), "w") as f:
            json.dump(config_content, f)
        
        with open(os.path.join(model_dir, "adapter_model.bin"), "w") as f:
            f.write("dummy model content")
        
        # Test that the model passes all security checks
        try:
            # Path validation
            PathValidator.is_safe_path(model_dir)
            
            # Model validation
            ModelValidator.validate_model_directory(model_dir)
            
            # File operations
            config = SecureFileHandler.safe_read_json(
                os.path.join(model_dir, "adapter_config.json")
            )
            assert config["base_model_name_or_path"] == "facebook/esm2_t33_650M_UR50D"
            
        except SecurityError as e:
            pytest.fail(f"Valid model failed security checks: {e}")

    def test_security_error_handling(self):
        """Test that security errors are properly handled and logged."""
        # Test various security violations
        security_violations = [
            ("Path traversal", lambda: PathValidator.is_safe_path("../../../etc/passwd")),
            ("Invalid model name", lambda: PathValidator.validate_model_name("model/with/slash")),
            ("Empty filename", lambda: PathValidator.sanitize_filename("")),
        ]
        
        for description, violation_func in security_violations:
            with pytest.raises(SecurityError):
                violation_func()


if __name__ == "__main__":
    pytest.main([__file__]) 