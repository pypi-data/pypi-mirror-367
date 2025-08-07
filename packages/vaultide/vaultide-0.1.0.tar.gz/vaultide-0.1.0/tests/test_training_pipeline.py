#!/usr/bin/env python3
"""
Tests for the training pipeline module.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch, mock_open
import pandas as pd
import json

# Remove module-level mocking - will use function-level mocking instead
# import sys
# from unittest.mock import MagicMock

# # Create mock modules
# mock_esm2 = MagicMock()
# mock_torch = MagicMock()
# mock_transformers = MagicMock()

# # Mock torch tensor
# mock_tensor = MagicMock()
# mock_tensor.item.return_value = 0
# mock_torch.tensor.return_value = mock_tensor

# # Mock transformers components
# mock_auto_tokenizer = MagicMock()
# mock_auto_model = MagicMock()
# mock_auto_model_class = MagicMock()

# # Set up the mock modules
# sys.modules['esm2'] = mock_esm2
# sys.modules['vaultide.esm2'] = mock_esm2
# sys.modules['vaultide.esm2.training_pipeline'] = mock_esm2
# sys.modules['torch'] = mock_torch
# sys.modules['transformers'] = mock_transformers
# sys.modules['transformers.AutoTokenizer'] = mock_auto_tokenizer
# sys.modules['transformers.AutoModel'] = mock_auto_model
# sys.modules['transformers.AutoModelForSequenceClassification'] = mock_auto_model_class

# # Mock the training pipeline functions
# mock_esm2.create_dataset = MagicMock()
# mock_esm2.run_full_pipeline = MagicMock()

# def mock_get_model_name(size):
#     if size in mock_esm2.MODEL_SIZE_MAPPING:
#         return mock_esm2.MODEL_SIZE_MAPPING[size]
#     else:
#         raise ValueError(f"Invalid model size: {size}")

# mock_esm2.get_model_name = MagicMock(side_effect=mock_get_model_name)

# mock_esm2.MODEL_SIZE_MAPPING = {
#     '8m': 'facebook/esm2_t6_8M_UR50D',
#     '35m': 'facebook/esm2_t12_35M_UR50D',
#     '150m': 'facebook/esm2_t30_150M_UR50D',
#     '650m': 'facebook/esm2_t33_650M_UR50D',
#     '3b': 'facebook/esm2_t36_3B_UR50D',
#     '15b': 'facebook/esm2_t48_15B_UR50D',
# }

# # Create a mock dataset class
# class MockDataset:
#     def __init__(self, *args, **kwargs):
#         # Check if the file contains required columns
#         if 'invalid.csv' in str(args[0]) if args else False:
#             raise ValueError("Invalid dataset format")
        
#         self.sequence_column = kwargs.get('sequence_column', 'window')
#         self.label_column = kwargs.get('label_column', 'label')
#         self._len = 4  # Mock length
    
#     def __len__(self):
#         return self._len
    
#     def __getitem__(self, idx):
#         return {
#             'input_ids': mock_torch.tensor([[1, 2, 3, 4, 5]]),
#             'attention_mask': mock_torch.tensor([[1, 1, 1, 1, 1]]),
#             'labels': mock_torch.tensor([0])
#         }

# mock_esm2.EnhancedProteinSequenceDataset = MockDataset

# Import the mocked functions
from vaultide.esm2.training_pipeline import create_dataset, run_full_pipeline, get_model_name, MODEL_SIZE_MAPPING, EnhancedProteinSequenceDataset


class TestTrainingPipeline:
    """Test cases for training pipeline functions."""

    def test_get_model_name(self):
        """Test model name retrieval for different model sizes."""
        # Test all supported model sizes
        for size, expected_name in MODEL_SIZE_MAPPING.items():
            model_name = get_model_name(size)
            assert model_name == expected_name
        
        # Test invalid model size
        with pytest.raises(ValueError, match="Invalid model_size"):
            get_model_name("invalid_size")

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_protein_sequence_dataset_ptm_format(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer, csv_files):
        """Test protein sequence dataset with PTM format."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Test with PTM format (window column)
        train_loader, val_loader, test_loader, tokenizer = create_dataset(
            batch_size=16,
            model_name="facebook/esm2_t33_650M_UR50D",
            train_data_path=csv_files['train'],
            val_data_path=csv_files['val'],
            test_data_path=csv_files['test'],
            sequence_column='window',
            label_column='label'
        )
        
        # Verify that the dataloaders were created
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
        assert tokenizer is not None

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_protein_sequence_dataset_custom_columns(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer, csv_files):
        """Test protein sequence dataset with custom column names."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Test with custom column names
        train_loader, val_loader, test_loader, tokenizer = create_dataset(
            batch_size=16,
            model_name="facebook/esm2_t33_650M_UR50D",
            train_data_path=csv_files['train'],
            val_data_path=csv_files['val'],
            test_data_path=csv_files['test'],
            sequence_column='window',
            label_column='label'
        )
        
        # Verify that the dataloaders were created
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
        assert tokenizer is not None

    def test_protein_sequence_dataset_invalid_format(self, temp_dir):
        """Test protein sequence dataset with invalid CSV format."""
        # Create an invalid CSV file
        invalid_csv = os.path.join(temp_dir, 'invalid.csv')
        with open(invalid_csv, 'w') as f:
            f.write("id,value\n1,0.5\n2,0.8")
        
        with pytest.raises(ValueError, match="Could not detect sequence column"):
            create_dataset(
                batch_size=16,
                model_name="facebook/esm2_t33_650M_UR50D",
                train_data_path=invalid_csv,
                val_data_path=invalid_csv,
                test_data_path=invalid_csv
            )

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_enhanced_protein_sequence_dataset(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer, csv_files):
        """Test enhanced protein sequence dataset with features."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Test enhanced dataset with features
        train_loader, val_loader, test_loader, tokenizer = create_dataset(
            batch_size=16,
            model_name="facebook/esm2_t33_650M_UR50D",
            train_data_path=csv_files['train'],
            val_data_path=csv_files['val'],
            test_data_path=csv_files['test'],
            sequence_column='window',
            label_column='label'
        )
        
        # Verify that the dataloaders were created
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
        assert tokenizer is not None

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_enhanced_protein_sequence_dataset_no_position(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer, csv_files, temp_dir):
        """Test enhanced protein sequence dataset without position column."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Create CSV without position column
        no_position_csv = os.path.join(temp_dir, 'no_position.csv')
        df = pd.DataFrame({
            'protein_id': ['Q86U44', 'Q8N2W9'],
            'window': ['XXXXXMSDTWSSIQAHKKQLDSLRERLQRRRKQ', 'XXXXXXXXMAAELVEAKNMVMSFRVSDLQMLLG'],
            'label': [0, 1]
        })
        df.to_csv(no_position_csv, index=False)
        
        # Test dataset creation without position column
        train_loader, val_loader, test_loader, tokenizer = create_dataset(
            batch_size=16,
            model_name="facebook/esm2_t33_650M_UR50D",
            train_data_path=no_position_csv,
            val_data_path=no_position_csv,
            test_data_path=no_position_csv,
            sequence_column='window',
            label_column='label'
        )
        
        # Verify that the dataloaders were created
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
        assert tokenizer is not None

    def test_enhanced_protein_sequence_dataset_missing_features(self, temp_dir):
        """Test enhanced protein sequence dataset with missing required features."""
        # Create CSV with missing required columns
        missing_features_csv = os.path.join(temp_dir, 'missing_features.csv')
        with open(missing_features_csv, 'w') as f:
            f.write("id,value\n1,0.5\n2,0.8")
        
        with pytest.raises(ValueError, match="Could not detect sequence column"):
            create_dataset(
                batch_size=16,
                model_name="facebook/esm2_t33_650M_UR50D",
                train_data_path=missing_features_csv,
                val_data_path=missing_features_csv,
                test_data_path=missing_features_csv
            )

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_create_dataset_mocked(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer):
        """Test dataset creation with mocked components."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Create temporary CSV files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame({
                'window': ['XXXXXMSDTWSSIQAHKKQLDSLRERLQRRRKQ'],
                'position': [12],
                'protein_id': ['Q86U44'],
                'label': [0]
            })
            df.to_csv(f.name, index=False)
            temp_csv = f.name
        
        try:
            # Test dataset creation
            train_loader, val_loader, test_loader, tokenizer = create_dataset(
                batch_size=16,
                model_name="facebook/esm2_t33_650M_UR50D",
                train_data_path=temp_csv,
                val_data_path=temp_csv,
                test_data_path=temp_csv,
                sequence_column='window',
                label_column='label'
            )
            
            # Verify that the dataloaders were created
            assert train_loader is not None
            assert val_loader is not None
            assert test_loader is not None
            assert tokenizer is not None
            
        finally:
            os.unlink(temp_csv)

    @patch('vaultide.esm2.training_pipeline.AutoTokenizer')
    @patch('vaultide.esm2.training_pipeline.AutoModel')
    @patch('vaultide.esm2.training_pipeline.AutoModelForSequenceClassification')
    @patch('vaultide.esm2.training_pipeline.DataLoader')
    def test_create_dataset_enhanced_features(self, mock_dataloader, mock_model_class, mock_model, mock_tokenizer):
        """Test dataset creation with enhanced features."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the dataloader with proper iterator behavior
        mock_dataloader_instance = MagicMock()
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([MagicMock()])  # Return a non-empty iterator
        mock_dataloader_instance.__iter__.return_value = mock_iterator
        mock_dataloader.return_value = mock_dataloader_instance
        
        # Create temporary CSV files with enhanced features
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame({
                'window': ['XXXXXMSDTWSSIQAHKKQLDSLRERLQRRRKQ'],
                'position': [12],
                'protein_id': ['Q86U44'],
                'label': [0]
            })
            df.to_csv(f.name, index=False)
            temp_csv = f.name
        
        try:
            # Test dataset creation with enhanced features
            train_loader, val_loader, test_loader, tokenizer = create_dataset(
                batch_size=16,
                model_name="facebook/esm2_t33_650M_UR50D",
                train_data_path=temp_csv,
                val_data_path=temp_csv,
                test_data_path=temp_csv,
                sequence_column='window',
                label_column='label'
            )
            
            # Verify that the dataloaders were created
            assert train_loader is not None
            assert val_loader is not None
            assert test_loader is not None
            assert tokenizer is not None
            
        finally:
            os.unlink(temp_csv)


class TestModelSizeMapping:
    """Test cases for model size mapping."""

    def test_model_size_mapping_completeness(self):
        """Test that all model sizes are properly mapped."""
        expected_sizes = ['8m', '35m', '150m', '650m', '3b', '15b']
        for size in expected_sizes:
            assert size in MODEL_SIZE_MAPPING
            model_name = get_model_name(size)
            assert model_name is not None
            assert isinstance(model_name, str)

    def test_model_size_mapping_values(self):
        """Test that model size mapping returns correct values."""
        expected_mappings = {
            '8m': 'facebook/esm2_t6_8M_UR50D',
            '35m': 'facebook/esm2_t12_35M_UR50D',
            '150m': 'facebook/esm2_t30_150M_UR50D',
            '650m': 'facebook/esm2_t33_650M_UR50D',
            '3b': 'facebook/esm2_t36_3B_UR50D',
            '15b': 'facebook/esm2_t48_15B_UR50D',
        }
        
        for size, expected_name in expected_mappings.items():
            actual_name = get_model_name(size)
            assert actual_name == expected_name 