"""
Pytest configuration and fixtures for vaultide tests.
"""

import pytest
import tempfile
import os
import shutil
import pandas as pd


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_ptm_data():
    """Create sample PTM prediction template data."""
    return {
        'protein_id': ['Q86U44', 'Q86U44', 'Q8N2W9', 'Q8N2W9'],
        'window': ['XXXXXMSDTWSSIQAHKKQLDSLRERLQRRRKQ', 
                  'AEKKGPGEVAGTVTGQKRRAEQDSTTVAAFASS',
                  'XXXXXXXXMAAELVEAKNMVMSFRVSDLQMLLG',
                  'DLQMLLGFVGRSKSGLKHELVTRALQLVQFDCS'],
        'position': [12, 177, 9, 35],
        'label': [0, 1, 0, 1]
    }


@pytest.fixture
def csv_files(temp_dir, sample_ptm_data):
    """Create test CSV files."""
    train_file = os.path.join(temp_dir, 'train.csv')
    val_file = os.path.join(temp_dir, 'val.csv')
    test_file = os.path.join(temp_dir, 'test.csv')
    
    df = pd.DataFrame(sample_ptm_data)
    df.to_csv(train_file, index=False)
    df.to_csv(val_file, index=False)
    df.to_csv(test_file, index=False)
    
    return {
        'train': train_file,
        'val': val_file,
        'test': test_file
    }


@pytest.fixture
def mock_training_results():
    """Mock training pipeline results."""
    return {
        'baseline_metrics': {
            'auroc': 0.7234,
            'auprc': 0.3456,
            'mcc': 0.2345
        },
        'final_metrics': {
            'auroc': 0.8567,
            'auprc': 0.5678,
            'mcc': 0.4567
        },
        'lora_metrics': {
            'model_path': '/path/to/trained/model'
        },
        'training_summary': {
            'pipeline_completed': True,
            'model_paths': {
                'lora_model_path': '/path/to/trained/model'
            }
        }
    } 