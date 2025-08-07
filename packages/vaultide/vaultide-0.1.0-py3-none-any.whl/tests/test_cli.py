#!/usr/bin/env python3
"""
Unit tests for the Vaultide CLI.

These tests mock the actual model loading and training steps to focus on CLI functionality,
argument parsing, data validation, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import sys
import pandas as pd
from pathlib import Path
import json
import argparse

# Add the parent directory to the path so we can import the CLI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vaultide.cli import VaultideCLI, main, FeatureValidator, Esm2FeatureValidator


class TestVaultideCLI:
    """Test cases for the VaultideCLI class."""

    def test_cli_initialization(self, temp_dir):
        """Test CLI initialization and directory creation."""
        # Mock the DEFAULT_LORA_BASE to use temp_dir
        with patch('vaultide.cli.cli.DEFAULT_LORA_BASE', temp_dir):
            cli = VaultideCLI()
            
            # Check that the base directory was created
            assert os.path.exists(temp_dir)
            
            # Check that config was loaded
            assert isinstance(cli.config, dict)

    def test_load_config_nonexistent(self):
        """Test loading config from non-existent file."""
        cli = VaultideCLI('/nonexistent/config.yaml')
        assert cli.config == {}

    def test_load_config_valid_yaml(self, temp_dir):
        """Test loading config from valid YAML file."""
        config_file = os.path.join(temp_dir, 'config.yaml')
        config_data = {'default_model': 'esm2', 'default_size': '650m'}
        
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        cli = VaultideCLI(config_file)
        assert cli.config == config_data

    def test_load_config_invalid_yaml(self, temp_dir):
        """Test loading config from invalid YAML file."""
        config_file = os.path.join(temp_dir, 'config.yaml')
        
        with open(config_file, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        cli = VaultideCLI(config_file)
        assert cli.config == {}

    def test_save_config(self, temp_dir):
        """Test saving configuration to file."""
        config_file = os.path.join(temp_dir, 'config.yaml')
        cli = VaultideCLI(config_file)
        cli.config = {'test_key': 'test_value'}
        
        cli.save_config()
        
        assert os.path.exists(config_file)
        with open(config_file, 'r') as f:
            import yaml
            loaded_config = yaml.safe_load(f)
            assert loaded_config == {'test_key': 'test_value'}

    def test_get_model_properties(self):
        """Test model properties retrieval."""
        cli = VaultideCLI()
        
        # Test ESM-2 model properties
        props = cli.get_model_properties('esm2', '650m')
        assert props['model_name'] == 'facebook/esm2_t33_650M_UR50D'
        
        # Test default model
        props = cli.get_model_properties('esm2')
        assert props['model_name'] == 'facebook/esm2_t33_650M_UR50D'
        
        # Test unknown model type
        props = cli.get_model_properties('unknown')
        assert props['model_name'] == 'facebook/esm2_t33_650M_UR50D'

    def test_get_feature_validator(self):
        """Test feature validator retrieval."""
        cli = VaultideCLI()
        
        # Test valid model type
        validator = cli.get_feature_validator('esm2')
        assert isinstance(validator, Esm2FeatureValidator)
        
        # Test invalid model type
        with pytest.raises(ValueError, match="Unknown model type"):
            cli.get_feature_validator('unknown')

    def test_validate_dataset_features(self, csv_files):
        """Test dataset feature validation."""
        cli = VaultideCLI()
        
        features = {'sequence': 'window', 'label': 'label'}
        validated = cli.validate_dataset_features('esm2', [csv_files['train']], features)
        
        assert validated['sequence'] == 'window'
        assert validated['label'] == 'label'

    def test_validate_dataset_features_missing_file(self):
        """Test feature validation with missing file."""
        cli = VaultideCLI()
        
        features = {'sequence': 'window', 'label': 'label'}
        with pytest.raises(ValueError, match="Data file not found"):
            cli.validate_dataset_features('esm2', ['/nonexistent/file.csv'], features)

    def test_train_model_success(self, csv_files, mock_training_results):
        """Test successful model training."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'esm2'
        args.model_size = '650m'
        args.train_data = csv_files['train']
        args.val_data = csv_files['val']
        args.test_data = csv_files['test']
        args.baseline_batch_size = 16
        args.lora_batch_size = 8
        args.epochs = 5
        args.learning_rate = 1e-4
        args.lora_r = 8
        args.lora_alpha = 16
        args.no_baseline = False
        args.sequence_column = None
        args.label_column = 'label'
        args.name = None

        with patch('vaultide.esm2.training_pipeline.run_full_pipeline') as mock_pipeline:
            mock_pipeline.return_value = mock_training_results
            
            result = cli.train_model(args)
            
            assert result == mock_training_results
            mock_pipeline.assert_called_once()

    def test_train_model_feature_validation_failure(self):
        """Test training with feature validation failure."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'esm2'
        args.train_data = '/nonexistent/train.csv'
        args.val_data = '/nonexistent/val.csv'
        args.test_data = '/nonexistent/test.csv'
        args.sequence_column = None
        args.label_column = 'label'
        
        result = cli.train_model(args)
        assert result is None

    def test_train_model_unknown_type(self):
        """Test training with unknown model type."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'unknown'
        args.train_data = 'train.csv'
        args.val_data = 'val.csv'
        args.test_data = 'test.csv'
        
        result = cli.train_model(args)
        assert result is None

    def test_train_esm2_validation(self, csv_files, mock_training_results):
        """Test ESM-2 training argument validation."""
        cli = VaultideCLI()
        
        # Create mock args
        args = MagicMock()
        args.model_type = 'esm2'
        args.model_size = '650m'
        args.train_data = csv_files['train']
        args.val_data = csv_files['val']
        args.test_data = csv_files['test']
        args.baseline_batch_size = 16
        args.lora_batch_size = 8
        args.epochs = 5
        args.learning_rate = 1e-4
        args.lora_r = 8
        args.lora_alpha = 16
        args.no_baseline = False
        args.sequence_column = None
        args.label_column = 'label'
        args.name = None

        # Mock the training pipeline
        with patch('vaultide.esm2.training_pipeline.run_full_pipeline') as mock_pipeline:
            mock_pipeline.return_value = mock_training_results
            
            # Create validated features dictionary
            validated_features = {
                'sequence': 'window',
                'label': 'label'
            }
            
            result = cli.train_esm2(args, validated_features)
            
            # Verify pipeline was called with correct arguments
            mock_pipeline.assert_called_once()
            call_args = mock_pipeline.call_args[1]
            
            assert call_args['model_size'] == '650m'
            assert call_args['train_data_path'] == csv_files['train']
            assert call_args['val_data_path'] == csv_files['val']
            assert call_args['test_data_path'] == csv_files['test']
            assert call_args['train_baseline'] == True
            assert call_args['features'] == validated_features

    def test_train_esm2_missing_files(self):
        """Test ESM-2 training with missing data files."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'esm2'
        args.model_size = '650m'
        args.train_data = '/nonexistent/train.csv'
        args.val_data = '/nonexistent/val.csv'
        args.test_data = '/nonexistent/test.csv'
        
        # Create validated features dictionary
        validated_features = {
            'sequence': 'window',
            'label': 'label'
        }
        
        result = cli.train_esm2(args, validated_features)
        assert result is None

    def test_train_custom_missing_paths(self):
        """Test custom training with missing data paths."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.train_data = None
        args.val_data = None
        args.test_data = None
        
        validated_features = {'sequence': 'window', 'label': 'label'}
        
        result = cli.train_custom(args, validated_features)
        assert result is None

    def test_list_models(self):
        """Test listing available models."""
        cli = VaultideCLI()
        
        # Test standard output
        with patch('sys.stdout') as mock_stdout:
            args = MagicMock()
            args.json = False
            cli.list_models(args)
            mock_stdout.write.assert_called()
        
        # Test JSON output
        with patch('sys.stdout') as mock_stdout:
            args = MagicMock()
            args.json = True
            cli.list_models(args)
            mock_stdout.write.assert_called()

    def test_list_loras_empty_directory(self, temp_dir):
        """Test listing LoRAs from empty directory."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.lora_base = temp_dir
        args.json = False
        
        with patch('sys.stdout') as mock_stdout:
            cli.list_loras(args)
            mock_stdout.write.assert_called()

    def test_list_loras_with_models(self, temp_dir):
        """Test listing LoRAs with existing models."""
        cli = VaultideCLI()
        
        # Create a mock LoRA directory structure
        lora_dir = os.path.join(temp_dir, 'esm2', 'test-model')
        os.makedirs(lora_dir, exist_ok=True)
        
        # Create mock LoRA files
        with open(os.path.join(lora_dir, 'adapter_model.bin'), 'w') as f:
            f.write('mock')
        
        # Create adapter config
        config_data = {
            'base_model_name_or_path': 'facebook/esm2_t33_650M_UR50D',
            'model_id': 'test-model'
        }
        with open(os.path.join(lora_dir, 'adapter_config.json'), 'w') as f:
            json.dump(config_data, f)
        
        args = MagicMock()
        args.lora_base = temp_dir
        args.json = False
        
        with patch('sys.stdout') as mock_stdout:
            cli.list_loras(args)
            mock_stdout.write.assert_called()

    def test_extract_model_info(self, temp_dir):
        """Test extracting model information from config files."""
        cli = VaultideCLI()
        
        # Create a mock model directory with config
        model_dir = os.path.join(temp_dir, 'test-model')
        os.makedirs(model_dir, exist_ok=True)
        
        config_data = {
            'model_size': '650m',
            'task': 'sumoylation',
            'num_epochs': 10,
            'learning_rate': 1e-4
        }
        
        with open(os.path.join(model_dir, 'config.json'), 'w') as f:
            json.dump(config_data, f)
        
        info = cli.extract_model_info(model_dir, 'test-model')
        assert info is not None
        assert 'training_params' in info
        assert 'size: 650m' in info['training_params']

    def test_extract_model_info_no_config(self, temp_dir):
        """Test extracting model info when no config exists."""
        cli = VaultideCLI()
        
        # Create empty model directory
        model_dir = os.path.join(temp_dir, 'test-model')
        os.makedirs(model_dir, exist_ok=True)
        
        info = cli.extract_model_info(model_dir, 'test-model')
        # Should return a dict with training_date even if no config exists
        assert info is not None
        assert 'training_date' in info

    def test_is_custom_name(self):
        """Test custom name detection."""
        cli = VaultideCLI()
        
        # Test auto-generated names
        assert not cli._is_custom_name('a1b2c3d4')  # 8 hex chars
        assert not cli._is_custom_name('a1b2c3d4-e5f6-7890-abcd-ef1234567890')  # UUID
        
        # Test custom names
        assert cli._is_custom_name('my-custom-model')
        assert cli._is_custom_name('model_v1')
        assert cli._is_custom_name('test123')

    def test_get_display_name(self):
        """Test display name generation."""
        cli = VaultideCLI()
        
        # Test UUID display
        uuid = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        assert cli._get_display_name(uuid) == 'a1b2c3d4'
        
        # Test short hex
        short_hex = 'a1b2c3d4'
        assert cli._get_display_name(short_hex) == 'a1b2c3d4'
        
        # Test custom name
        custom = 'my-custom-model'
        assert cli._get_display_name(custom) == 'my-custom-model'

    def test_predict_esm2_success(self, temp_dir):
        """Test successful ESM-2 prediction."""
        cli = VaultideCLI()
        
        # Create mock LoRA directory
        lora_dir = os.path.join(temp_dir, 'esm2', 'test-lora')
        os.makedirs(lora_dir, exist_ok=True)
        
        # Create mock LoRA files
        with open(os.path.join(lora_dir, 'adapter_model.bin'), 'w') as f:
            f.write('mock')
        
        # Create adapter config
        config_data = {
            'base_model_name_or_path': 'facebook/esm2_t33_650M_UR50D',
            'model_type': 'esm2'
        }
        with open(os.path.join(lora_dir, 'adapter_config.json'), 'w') as f:
            json.dump(config_data, f)
        
        args = MagicMock()
        args.lora = 'test-lora'
        args.sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        args.lora_strength = 1.0
        args.verbose = False
        args.json = False
        args.output_file = None
        
        mock_result = {
            'prediction': 0.85,
            'confidence': 0.92,
            'base_model': 'facebook/esm2_t33_650M_UR50D',
            'timestamp': '2023-01-01T00:00:00Z'
        }
        
        with patch('vaultide.cli.cli.DEFAULT_LORA_BASE', temp_dir), \
             patch('builtins.__import__') as mock_import:
            
            # Mock the inference module
            mock_inference_module = MagicMock()
            mock_inference_module.run_inference = MagicMock(return_value=mock_result)
            mock_inference_module.validate_sequence = MagicMock(return_value=True)
            
            def mock_import_side_effect(name, *args, **kwargs):
                if name == 'vaultide.esm2.inference':
                    return mock_inference_module
                return MagicMock()
            
            mock_import.side_effect = mock_import_side_effect
            
            result = cli.predict_esm2(args)
            
            assert result == mock_result
            mock_inference_module.run_inference.assert_called_once()
            mock_inference_module.validate_sequence.assert_called_once_with('MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG')

    def test_predict_esm2_lora_not_found(self):
        """Test ESM-2 prediction when LoRA is not found."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.lora = 'nonexistent-lora'
        args.sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        args.lora_strength = 1.0
        args.verbose = False
        args.json = False
        args.output_file = None
        
        with patch('vaultide.cli.cli.DEFAULT_LORA_BASE', '/nonexistent/path'), \
             patch('builtins.__import__') as mock_import:
            
            # Mock the inference module
            mock_inference_module = MagicMock()
            mock_import.side_effect = lambda name, *args, **kwargs: mock_inference_module if name == 'vaultide.esm2.inference' else MagicMock()
            
            result = cli.predict_esm2(args)
            assert result is None

    def test_predict_esm2_invalid_sequence(self):
        """Test ESM-2 prediction with invalid sequence."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.lora = 'test-lora'
        args.sequence = 'INVALID_SEQUENCE_123'
        args.lora_strength = 1.0
        args.verbose = False
        args.json = False
        args.output_file = None
        
        with patch('builtins.__import__') as mock_import:
            # Mock the inference module
            mock_inference_module = MagicMock()
            mock_inference_module.validate_sequence = MagicMock(return_value=False)
            mock_import.side_effect = lambda name, *args, **kwargs: mock_inference_module if name == 'vaultide.esm2.inference' else MagicMock()
            
            result = cli.predict_esm2(args)
            assert result is None

    def test_predict_esm2_inference_failure(self, temp_dir):
        """Test ESM-2 prediction when inference fails."""
        cli = VaultideCLI()
        
        # Create mock LoRA directory
        lora_dir = os.path.join(temp_dir, 'esm2', 'test-lora')
        os.makedirs(lora_dir, exist_ok=True)
        
        # Create mock LoRA files
        with open(os.path.join(lora_dir, 'adapter_model.bin'), 'w') as f:
            f.write('mock')
        
        # Create adapter config
        config_data = {
            'base_model_name_or_path': 'facebook/esm2_t33_650M_UR50D',
            'model_type': 'esm2'
        }
        with open(os.path.join(lora_dir, 'adapter_config.json'), 'w') as f:
            json.dump(config_data, f)
        
        args = MagicMock()
        args.lora = 'test-lora'
        args.sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        args.lora_strength = 1.0
        args.verbose = False
        args.json = False
        args.output_file = None
        
        with patch('vaultide.cli.cli.DEFAULT_LORA_BASE', temp_dir), \
             patch('builtins.__import__') as mock_import:
            
            # Mock the inference module
            mock_inference_module = MagicMock()
            mock_inference_module.validate_sequence = MagicMock(return_value=True)
            mock_inference_module.run_inference = MagicMock(side_effect=Exception("Inference failed"))
            mock_import.side_effect = lambda name, *args, **kwargs: mock_inference_module if name == 'vaultide.esm2.inference' else MagicMock()
            
            result = cli.predict_esm2(args)
            assert result is None

    def test_output_prediction_results_json(self, temp_dir):
        """Test JSON output formatting for predictions."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.json = True
        args.output_file = None
        args.lora = 'test-lora'
        args.lora_strength = 1.0
        
        result = {
            'prediction': 0.85,
            'confidence': 0.92,
            'base_model': 'facebook/esm2_t33_650M_UR50D',
            'timestamp': '2023-01-01T00:00:00Z'
        }
        
        sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        
        with patch('sys.stdout') as mock_stdout:
            cli._output_prediction_results(result, args, sequence)
            mock_stdout.write.assert_called()

    def test_output_prediction_results_standard(self):
        """Test standard output formatting for predictions."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.json = False
        args.verbose = False
        args.output_file = None
        args.lora = 'test-lora'
        args.lora_strength = 1.0
        
        result = {
            'prediction': 0.85,
            'confidence': 0.92,
            'base_model': 'facebook/esm2_t33_650M_UR50D',
            'timestamp': '2023-01-01T00:00:00Z'
        }
        
        sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        
        with patch('sys.stdout') as mock_stdout:
            cli._output_prediction_results(result, args, sequence)
            mock_stdout.write.assert_called()

    def test_output_prediction_results_with_file(self, temp_dir):
        """Test prediction output with file saving."""
        cli = VaultideCLI()
        
        output_file = os.path.join(temp_dir, 'output.txt')
        
        args = MagicMock()
        args.json = False
        args.verbose = True
        args.output_file = output_file
        args.lora = 'test-lora'
        args.lora_strength = 1.0
        
        result = {
            'prediction': 0.85,
            'confidence': 0.92,
            'base_model': 'facebook/esm2_t33_650M_UR50D',
            'timestamp': '2023-01-01T00:00:00Z'
        }
        
        sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
        
        cli._output_prediction_results(result, args, sequence)
        
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            assert 'test-lora' in content
            assert '0.8500' in content

    def test_serve_model_esm2(self, temp_dir):
        """Test serving ESM-2 model."""
        cli = VaultideCLI()
        
        # Create mock LoRA directory
        lora_dir = os.path.join(temp_dir, 'esm2', 'test-lora')
        os.makedirs(lora_dir, exist_ok=True)
        
        # Create mock LoRA files
        with open(os.path.join(lora_dir, 'adapter_model.bin'), 'w') as f:
            f.write('mock')
        
        # Create adapter config
        config_data = {
            'base_model_name_or_path': 'facebook/esm2_t33_650M_UR50D',
            'model_type': 'esm2'
        }
        with open(os.path.join(lora_dir, 'adapter_config.json'), 'w') as f:
            json.dump(config_data, f)
        
        args = MagicMock()
        args.model_type = 'esm2'
        args.lora = 'test-lora'
        args.lora_strength = 1.0
        args.host = '127.0.0.1'
        args.port = 8000
        args.verbose = False
        
        with patch('vaultide.cli.cli.DEFAULT_LORA_BASE', temp_dir), \
             patch('vaultide.esm2.serve_esm2') as mock_serve:
            cli.serve_model(args)
            mock_serve.assert_called_once_with(
                lora_name='test-lora',
                lora_strength=1.0,
                host='127.0.0.1',
                port=8000,
                verbose=False
            )

    def test_serve_model_unknown_type(self):
        """Test serving unknown model type."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'unknown'
        
        result = cli.serve_model(args)
        assert result is None

    def test_serve_model_import_error(self):
        """Test serving model with import error."""
        cli = VaultideCLI()
        
        args = MagicMock()
        args.model_type = 'esm2'
        args.lora = 'test-lora'
        args.lora_strength = 1.0
        args.host = '127.0.0.1'
        args.port = 8000
        args.verbose = False
        
        with patch('vaultide.esm2.serve_esm2', side_effect=ImportError("Module not found")):
            result = cli.serve_model(args)
            assert result is None

    def test_feature_agnostic_cli(self, csv_files, mock_training_results):
        """Test the new feature-agnostic CLI system."""
        cli = VaultideCLI()
        
        # Create mock args
        args = MagicMock()
        args.model_type = 'esm2'
        args.model_size = '650m'
        args.train_data = csv_files['train']
        args.val_data = csv_files['val']
        args.test_data = csv_files['test']
        args.baseline_batch_size = 16
        args.lora_batch_size = 8
        args.epochs = 5
        args.learning_rate = 1e-4
        args.lora_r = 8
        args.lora_alpha = 16
        args.no_baseline = False
        args.sequence_column = None
        args.label_column = 'label'
        args.name = None

        # Mock the training pipeline
        with patch('vaultide.esm2.training_pipeline.run_full_pipeline') as mock_pipeline:
            mock_pipeline.return_value = mock_training_results
            
            result = cli.train_model(args)
            
            # Verify pipeline was called with correct arguments
            mock_pipeline.assert_called_once()
            call_args = mock_pipeline.call_args[1]
            
            assert call_args['model_size'] == '650m'
            assert call_args['train_data_path'] == csv_files['train']
            assert call_args['val_data_path'] == csv_files['val']
            assert call_args['test_data_path'] == csv_files['test']
            assert call_args['train_baseline'] == True
            # Verify features are passed correctly
            assert 'features' in call_args
            assert call_args['features']['sequence'] == 'window'  # Auto-detected
            assert call_args['features']['label'] == 'label'

    def test_feature_validation_with_custom_columns(self, csv_files, mock_training_results):
        """Test feature validation with custom column names."""
        cli = VaultideCLI()
        
        # Create mock args with custom column names
        args = MagicMock()
        args.model_type = 'esm2'
        args.model_size = '650m'
        args.train_data = csv_files['train']
        args.val_data = csv_files['val']
        args.test_data = csv_files['test']
        args.baseline_batch_size = 16
        args.lora_batch_size = 8
        args.epochs = 5
        args.learning_rate = 1e-4
        args.lora_r = 8
        args.lora_alpha = 16
        args.no_baseline = False
        args.sequence_column = 'window'  # Explicitly specify
        args.label_column = 'label'
        args.name = None

        # Mock the training pipeline
        with patch('vaultide.esm2.training_pipeline.run_full_pipeline') as mock_pipeline:
            mock_pipeline.return_value = mock_training_results
            
            result = cli.train_model(args)
            
            # Verify pipeline was called with correct arguments
            mock_pipeline.assert_called_once()
            call_args = mock_pipeline.call_args[1]
            
            # Verify features are passed correctly
            assert 'features' in call_args
            assert call_args['features']['sequence'] == 'window'
            assert call_args['features']['label'] == 'label'

    def test_feature_validation_error_handling(self):
        """Test feature validation error handling."""
        cli = VaultideCLI()
        
        # Create mock args with invalid data
        args = MagicMock()
        args.model_type = 'esm2'
        args.train_data = '/nonexistent/train.csv'
        args.val_data = '/nonexistent/val.csv'
        args.test_data = '/nonexistent/test.csv'
        args.sequence_column = None
        args.label_column = 'label'
        
        # Should return None due to file not found
        result = cli.train_model(args)
        assert result is None

    def test_feature_validator_registry(self):
        """Test that feature validators are properly registered."""
        from vaultide.cli import FEATURE_VALIDATORS
        
        # Check that ESM-2 validator is registered
        assert 'esm2' in FEATURE_VALIDATORS
        assert hasattr(FEATURE_VALIDATORS['esm2'], 'validate_features')
        assert hasattr(FEATURE_VALIDATORS['esm2'], 'get_feature_help')
        
        # Check that it has the correct required features
        validator = FEATURE_VALIDATORS['esm2']
        assert 'sequence' in validator.required_features
        assert 'label' in validator.required_features

    def test_feature_validator_help(self):
        """Test feature validator help text generation."""
        from vaultide.cli import FEATURE_VALIDATORS
        
        validator = FEATURE_VALIDATORS['esm2']
        help_text = validator.get_feature_help()
        
        assert 'Features for esm2 model:' in help_text
        assert 'Required features:' in help_text
        assert 'sequence:' in help_text
        assert 'label:' in help_text


class TestFeatureValidator:
    """Test cases for the FeatureValidator base class."""
    
    def test_feature_validator_initialization(self):
        """Test FeatureValidator initialization."""
        validator = FeatureValidator('test_model')
        assert validator.model_type == 'test_model'
        assert validator.required_features == set()
        assert validator.optional_features == set()
        assert validator.feature_descriptions == {}
    
    def test_feature_validator_validate_features_empty(self):
        """Test feature validation with empty features."""
        validator = FeatureValidator('test_model')
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('col1,col2\nvalue1,value2\n')
            csv_path = f.name
        
        try:
            features = {}
            result = validator.validate_features(csv_path, features)
            assert result == {}
        finally:
            os.unlink(csv_path)
    
    def test_feature_validator_validate_features_missing_file(self):
        """Test feature validation with missing file."""
        validator = FeatureValidator('test_model')
        
        with pytest.raises(ValueError, match="Could not read CSV file"):
            validator.validate_features('/nonexistent/file.csv', {})
    
    def test_feature_validator_get_feature_help(self):
        """Test feature help text generation."""
        validator = FeatureValidator('test_model')
        validator.required_features = {'feature1', 'feature2'}
        validator.optional_features = {'optional1'}
        validator.feature_descriptions = {
            'feature1': 'First required feature',
            'feature2': 'Second required feature',
            'optional1': 'Optional feature'
        }
        
        help_text = validator.get_feature_help()
        
        assert 'Features for test_model model:' in help_text
        assert 'Required features:' in help_text
        assert 'Optional features:' in help_text
        assert 'feature1: First required feature' in help_text
        assert 'feature2: Second required feature' in help_text
        assert 'optional1: Optional feature' in help_text


class TestEsm2FeatureValidator:
    """Test cases for the ESM-2 feature validator."""
    
    def test_esm2_validator_initialization(self):
        """Test ESM-2 validator initialization."""
        validator = Esm2FeatureValidator()
        assert validator.model_type == 'esm2'
        assert 'sequence' in validator.required_features
        assert 'label' in validator.required_features
        assert len(validator.optional_features) == 0
    
    def test_esm2_validator_auto_detection(self, csv_files):
        """Test ESM-2 feature auto-detection."""
        validator = Esm2FeatureValidator()
        
        features = {}
        result = validator.validate_features(csv_files['train'], features)
        
        assert result['sequence'] == 'window'  # Auto-detected
        assert result['label'] == 'label'  # Default
    
    def test_esm2_validator_custom_columns(self, csv_files):
        """Test ESM-2 validator with custom column names."""
        validator = Esm2FeatureValidator()
        
        features = {
            'sequence': 'window',
            'label': 'label'
        }
        result = validator.validate_features(csv_files['train'], features)
        
        assert result['sequence'] == 'window'
        assert result['label'] == 'label'
    
    def test_esm2_validator_missing_sequence_column(self, temp_dir):
        """Test ESM-2 validator with missing sequence column."""
        validator = Esm2FeatureValidator()
        
        # Create CSV without sequence-like columns
        csv_file = os.path.join(temp_dir, 'test.csv')
        with open(csv_file, 'w') as f:
            f.write('id,value\n1,test\n')
        
        features = {}
        
        with pytest.raises(ValueError, match="Could not detect sequence column"):
            validator.validate_features(csv_file, features)
    
    def test_esm2_validator_missing_label_column(self, temp_dir):
        """Test ESM-2 validator with missing label column."""
        validator = Esm2FeatureValidator()
        
        # Create CSV with sequence but no label
        csv_file = os.path.join(temp_dir, 'test.csv')
        with open(csv_file, 'w') as f:
            f.write('window,other\nMKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG,test\n')
        
        features = {'label': 'nonexistent'}
        
        with pytest.raises(ValueError, match="Label column 'nonexistent' not found"):
            validator.validate_features(csv_file, features)


# Note: TestArgumentParser class removed as it was testing argparse functionality
# which has been replaced with click-based CLI


# Note: TestMainFunction class removed as it was testing argparse functionality
# which has been replaced with click-based CLI. The click CLI behavior is different
# and these tests would need to be completely rewritten to work with click. 