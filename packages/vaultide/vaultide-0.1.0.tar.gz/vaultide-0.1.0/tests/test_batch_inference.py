#!/usr/bin/env python3
"""
Tests for the batch inference module.
"""

import os
import tempfile
import pytest
import pandas as pd
import json
from unittest.mock import MagicMock, patch, mock_open
import sys

# Remove module-level mocking - will use function-level mocking instead
# mock_torch = MagicMock()
# mock_torch.__version__ = "2.0.0"
# mock_torch.cuda.is_available.return_value = False  # Mock CUDA as unavailable
# sys.modules['torch'] = mock_torch
# sys.modules['transformers'] = MagicMock()
# sys.modules['peft'] = MagicMock()

from vaultide.esm2.batch_inference import (
    auto_detect_sequence_column,
    validate_csv_data,
    generate_metadata,
    run_batch_inference
)


class TestBatchInference:
    """Test cases for batch inference functions."""

    def test_auto_detect_sequence_column(self):
        """Test automatic sequence column detection."""
        # Test with exact matches
        df = pd.DataFrame({
            'sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'],
            'label': [1]
        })
        assert auto_detect_sequence_column(df) == 'sequence'
        
        # Test with window column (PTM format)
        df = pd.DataFrame({
            'window': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'],
            'label': [1]
        })
        assert auto_detect_sequence_column(df) == 'window'
        
        # Test with partial match
        df = pd.DataFrame({
            'protein_sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'],
            'label': [1]
        })
        assert auto_detect_sequence_column(df) == 'protein_sequence'
        
        # Test failure case
        df = pd.DataFrame({
            'id': [1],
            'value': [0.5],
            'label': [1]
        })
        with pytest.raises(ValueError, match="Could not detect sequence column"):
            auto_detect_sequence_column(df)

    def test_validate_csv_data(self):
        """Test CSV data validation."""
        # Valid data
        df = pd.DataFrame({
            'sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'],
            'label': [1]
        })
        
        df_cleaned, errors = validate_csv_data(df, 'sequence')
        assert len(df_cleaned) == 1
        assert len(errors) == 0
        
        # Invalid sequence
        df = pd.DataFrame({
            'sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG', 'INVALID123'],
            'label': [1, 0]
        })
        
        df_cleaned, errors = validate_csv_data(df, 'sequence')
        assert len(df_cleaned) == 1
        assert len(errors) == 1
        assert 'Invalid sequence' in errors[0]
        
        # Empty sequence - this should be filtered out
        df = pd.DataFrame({
            'sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG', ''],
            'label': [1, 0]
        })
        
        df_cleaned, errors = validate_csv_data(df, 'sequence')
        assert len(df_cleaned) == 1  # Only the valid sequence should remain
        assert len(errors) == 1
        assert 'Empty sequence' in errors[0]

    @patch('vaultide.esm2.batch_inference.os.path.exists')
    @patch('vaultide.esm2.batch_inference.os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data=b"test data")
    def test_generate_metadata(self, mock_open_file, mock_getsize, mock_exists):
        """Test metadata generation."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        
        # Create test data
        validation_errors = ["Error 1", "Error 2"]
        processing_stats = {
            "total_rows": 100,
            "valid_rows": 95,
            "invalid_rows": 5,
            "start_time": "2023-01-01T00:00:00",
            "end_time": "2023-01-01T00:01:00",
            "processing_time_seconds": 60.0
        }
        
        metadata = generate_metadata(
            lora_name="test_lora",
            input_csv_path="/path/to/input.csv",
            output_dir="/path/to/output",
            sequence_column="sequence",
            lora_strength=1.0,
            full_probabilities=False,
            batch_size=32,
            validation_errors=validation_errors,
            processing_stats=processing_stats
        )
        
        # Verify metadata structure
        assert metadata["metadata_version"] == "1.0"
        assert metadata["model"]["lora_name"] == "test_lora"
        assert metadata["model"]["lora_strength"] == 1.0
        assert metadata["model"]["batch_size"] == 32
        assert metadata["processing"]["error_count"] == 2
        assert len(metadata["processing"]["validation_errors"]) == 2

    @patch('vaultide.esm2.batch_inference.load_lora_model')
    @patch('vaultide.esm2.batch_inference.os.path.exists')
    @patch('vaultide.esm2.batch_inference.os.path.getsize')
    @patch('vaultide.esm2.batch_inference.os.makedirs')
    @patch('vaultide.esm2.batch_inference.pd.read_csv')
    @patch('builtins.open', new_callable=mock_open, read_data=b"test data")
    @patch('vaultide.esm2.batch_inference.json.dump')
    @patch('vaultide.esm2.batch_inference.torch.sigmoid')
    @patch('vaultide.esm2.batch_inference.torch.softmax')
    def test_run_batch_inference(self, mock_softmax, mock_sigmoid, mock_json_dump, mock_open_file, mock_read_csv, mock_makedirs, mock_getsize, mock_exists, mock_load_model):
        """Test batch inference execution."""
        # Mock the model loading
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_base_model_name = "facebook/esm2_t33_650M_UR50D"
        mock_load_model.return_value = (mock_model, mock_tokenizer, mock_base_model_name)
        
        # Mock file operations
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        # Ensure makedirs doesn't raise an error
        mock_makedirs.return_value = None
        
        # Mock CSV data
        test_df = pd.DataFrame({
            'sequence': ['MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'],
            'label': [1]
        })
        mock_read_csv.return_value = test_df
        
        # Mock tokenizer output
        mock_tokenizer.return_value = {
            'input_ids': MagicMock(),
            'attention_mask': MagicMock()
        }
        
        # Mock model output
        mock_outputs = MagicMock()
        mock_outputs.logits = MagicMock()
        mock_model.return_value = mock_outputs
        
        # Mock device - fix the device mocking
        mock_device = MagicMock()
        mock_parameter = MagicMock()
        mock_parameter.device = mock_device
        mock_model.parameters.return_value = iter([mock_parameter])
        
        # Mock torch operations
        mock_sigmoid.return_value = MagicMock()
        mock_sigmoid.return_value.item.return_value = 0.75
        mock_softmax.return_value = MagicMock()
        mock_softmax.return_value.__getitem__.return_value = MagicMock()
        mock_softmax.return_value.__getitem__().__getitem__.return_value = MagicMock()
        mock_softmax.return_value.__getitem__().__getitem__().item.return_value = 0.8
        
        # Run the function
        result = run_batch_inference(
            lora_name="test_lora",
            input_csv_path="/path/to/input.csv",
            output_dir="/tmp/test_output",  # Use /tmp instead of /path
            sequence_column="sequence"
        )
        
        # Verify the result
        assert result["success"] is True
        assert "output_csv" in result
        assert "metadata_file" in result
        assert "processing_stats" in result
        assert "validation_errors" in result
        assert "metadata" in result

    def test_run_batch_inference_file_not_found(self):
        """Test batch inference with non-existent input file."""
        with pytest.raises(FileNotFoundError, match="Input CSV file not found"):
            run_batch_inference(
                lora_name="test_lora",
                input_csv_path="/nonexistent/file.csv",
                output_dir="/tmp/test_output"  # Use /tmp instead of /path
            )

    def test_run_batch_inference_no_valid_sequences(self):
        """Test batch inference with no valid sequences."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Create CSV with invalid sequences
            df = pd.DataFrame({
                'sequence': ['INVALID123', 'ALSO_INVALID456'],
                'label': [1, 0]
            })
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="No valid sequences found"):
                run_batch_inference(
                    lora_name="test_lora",
                    input_csv_path=temp_file,
                    output_dir="/tmp/test_output"  # Use /tmp instead of /path
                )
        finally:
            os.unlink(temp_file) 