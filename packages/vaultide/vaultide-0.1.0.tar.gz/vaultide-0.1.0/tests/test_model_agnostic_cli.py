#!/usr/bin/env python3
"""
Test the model-agnostic CLI functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from vaultide.cli.cli import VaultideCLI
from vaultide.cli.features import FEATURE_VALIDATORS


class TestModelAgnosticCLI:
    """Test the model-agnostic CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cli = VaultideCLI()

    def test_get_model_properties_esm2(self):
        """Test getting ESM-2 model properties."""
        props = self.cli.get_model_properties("esm2", "650m")
        assert props["model_name"] == "facebook/esm2_t33_650M_UR50D"
        assert props["model_size"] == "650m"

    def test_get_model_properties_multimodal(self):
        """Test getting multimodal model properties."""
        props = self.cli.get_model_properties("multimodal", "medium")
        assert props["model_name"] == "your-model/medium-variant"
        assert props["model_size"] == "medium"

    def test_get_model_properties_unknown_defaults_to_esm2(self):
        """Test that unknown model types default to ESM-2."""
        with patch('vaultide.cli.cli.logger') as mock_logger:
            props = self.cli.get_model_properties("unknown_model", "650m")
            assert props["model_name"] == "facebook/esm2_t33_650M_UR50D"
            assert props["model_size"] == "650m"
            mock_logger.warning.assert_called_once()

    def test_get_feature_validator_esm2(self):
        """Test getting ESM-2 feature validator."""
        validator = self.cli.get_feature_validator("esm2")
        assert validator.model_type == "esm2"
        assert "sequence" in validator.required_features
        assert "label" in validator.required_features

    def test_get_feature_validator_multimodal(self):
        """Test getting multimodal feature validator."""
        validator = self.cli.get_feature_validator("multimodal")
        assert validator.model_type == "multimodal"
        assert "sequence" in validator.required_features
        assert "label" in validator.required_features
        assert "structure" in validator.required_features

    def test_get_feature_validator_unknown_raises_error(self):
        """Test that unknown model types raise an error."""
        with pytest.raises(ValueError, match="Unknown model type"):
            self.cli.get_feature_validator("unknown_model")

    def test_predict_model_routing(self):
        """Test that predict_model routes to correct model-specific function."""
        # Mock the model-specific prediction functions
        with patch.object(self.cli, 'predict_esm2') as mock_predict_esm2:
            mock_predict_esm2.return_value = {"prediction": 0.8}
            
            # Create mock args
            class MockArgs:
                def __init__(self, model_type):
                    self.model_type = model_type
                    self.lora = "test-model"
                    self.sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            
            args = MockArgs("esm2")
            result = self.cli.predict_model(args)
            
            # Verify the correct function was called
            mock_predict_esm2.assert_called_once_with(args)
            assert result == {"prediction": 0.8}

    def test_predict_model_unknown_type(self):
        """Test that unknown model types in predict_model show error."""
        class MockArgs:
            def __init__(self, model_type):
                self.model_type = model_type
        
        args = MockArgs("unknown_model")
        
        with patch('vaultide.cli.cli.logger') as mock_logger:
            result = self.cli.predict_model(args)
            
            assert result is None
            mock_logger.error.assert_called()

    def test_batch_predict_model_routing(self):
        """Test that batch_predict_model routes to correct model-specific function."""
        # Mock the model-specific batch prediction functions
        with patch.object(self.cli, 'batch_predict_esm2') as mock_batch_predict_esm2:
            mock_batch_predict_esm2.return_value = {"processed": 100}
            
            # Create mock args
            class MockArgs:
                def __init__(self, model_type):
                    self.model_type = model_type
                    self.lora = "test-model"
                    self.input_csv = "test.csv"
                    self.output_dir = "output"
            
            args = MockArgs("esm2")
            result = self.cli.batch_predict_model(args)
            
            # Verify the correct function was called
            mock_batch_predict_esm2.assert_called_once_with(args)
            assert result == {"processed": 100}

    def test_serve_model_routing(self):
        """Test that serve_model routes to correct model-specific function."""
        # Mock the model-specific serve functions
        with patch.object(self.cli, '_serve_esm2') as mock_serve_esm2:
            # Create mock args
            class MockArgs:
                def __init__(self, model_type):
                    self.model_type = model_type
                    self.lora = "test-model"
                    self.host = "127.0.0.1"
                    self.port = 8000
            
            args = MockArgs("esm2")
            self.cli.serve_model(args)
            
            # Verify the correct function was called
            mock_serve_esm2.assert_called_once_with(args)

    def test_list_models_includes_all_types(self):
        """Test that list_models includes all registered model types."""
        class MockArgs:
            def __init__(self):
                self.json = False
        
        args = MockArgs()
        
        # Mock the print function to capture output
        with patch('builtins.print') as mock_print:
            self.cli.list_models(args)
            
            # Get the printed output
            calls = mock_print.call_args_list
            output_lines = [call[0][0] for call in calls]
            
            # Check that both esm2 and multimodal models are listed
            output_text = '\n'.join(output_lines)
            assert 'esm2' in output_text
            assert 'multimodal' in output_text
            assert 'facebook/esm2_t33_650M_UR50D' in output_text
            assert 'your-model/medium-variant' in output_text

    def test_show_model_features_esm2(self):
        """Test showing features for ESM-2 model."""
        with patch('builtins.print') as mock_print:
            self.cli.show_model_features("esm2")
            
            # Verify that help text was printed
            calls = mock_print.call_args_list
            output_lines = [call[0][0] for call in calls]
            output_text = '\n'.join(output_lines)
            
            assert 'Features for esm2 model:' in output_text
            assert 'sequence' in output_text
            assert 'label' in output_text

    def test_show_model_features_unknown(self):
        """Test showing features for unknown model type."""
        with patch('vaultide.cli.cli.logger') as mock_logger:
            self.cli.show_model_features("unknown_model")
            
            # Verify error was logged
            mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__]) 