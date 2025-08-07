"""
ESMC Training Pipeline

This module provides training utilities for the ESMC model using the esm Python package.
"""

from uuid import uuid4
import pandas as pd
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import torch
import torch.nn as nn
import numpy as np
import esm.pretrained
from sklearn.metrics import roc_auc_score, average_precision_score, matthews_corrcoef
from tqdm import tqdm
import logging
import os
from datetime import datetime
from torchmetrics.classification import (
    BinaryAUROC,
    BinaryAveragePrecision,
    BinaryMatthewsCorrCoef,
)
from torchmetrics import MetricCollection
import json
from typing import Optional

from vaultide.config import get_lora_base_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vaultide")

MODEL_NAME = "ESMC_300M_202412"
# Use CUDA if available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Model size mapping for ESMC
MODEL_SIZE_MAPPING = {
    "300m": "ESMC_300M_202412",
    "600m": "ESMC_600M_202412",
}


def load_esmc_model(model_name: str):
    """
    Load ESMC model using the esm package.

    Args:
        model_name: ESMC model name

    Returns:
        Loaded ESMC model

    Raises:
        ValueError: If model_name is invalid
    """
    try:
        if model_name == "ESMC_300M_202412":
            model = esm.pretrained.ESMC_300M_202412()
        elif model_name == "ESMC_600M_202412":
            model = esm.pretrained.ESMC_600M_202412()
        else:
            raise ValueError(f"Unknown ESMC model: {model_name}")

        model = model.to(DEVICE)
        return model
    except Exception as e:
        raise ValueError(f"Failed to load ESMC model {model_name}: {e}")


def get_model_name(model_size: str) -> str:
    """
    Get the model name based on the model size.

    Args:
        model_size: ESMC model size (300m, 600m)

    Returns:
        The corresponding model name

    Raises:
        ValueError: If model_size is not one of the valid options
    """
    if model_size not in MODEL_SIZE_MAPPING:
        raise ValueError(
            f"Invalid model_size: {model_size}. Must be one of {list(MODEL_SIZE_MAPPING.keys())}"
        )
    return MODEL_SIZE_MAPPING[model_size]


class ESMCClassificationHead(nn.Module):
    """Classification head for ESMC models."""

    def __init__(self, hidden_size: int, num_classes: int = 2, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, pooled_output):
        pooled_output = self.dropout(pooled_output)
        return self.classifier(pooled_output)


class ESMCSequenceClassifier(nn.Module):
    """ESMC model with classification head."""

    def __init__(self, esmc_model, num_classes: int = 2, dropout: float = 0.1):
        super().__init__()
        self.esmc_model = esmc_model

        # Get the output size from the model using a real sequence
        with torch.no_grad():
            test_sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            encoded = esmc_model.tokenizer.encode_plus(
                test_sequence, return_tensors="pt"
            )
            # Ensure input is on the same device as the model
            device = next(esmc_model.parameters()).device
            input_ids = encoded["input_ids"].to(device)
            output = esmc_model(input_ids)
            # ESMC outputs embeddings with shape [batch_size, seq_len, hidden_size]
            hidden_size = output.embeddings.shape[-1]

        self.classification_head = ESMCClassificationHead(
            hidden_size, num_classes, dropout
        )

    def forward(self, input_ids, attention_mask=None):
        # Get ESMC representations
        outputs = self.esmc_model(input_ids)

        # ESMC outputs embeddings with shape [batch_size, seq_len, hidden_size]
        embeddings = outputs.embeddings  # Shape: [batch_size, seq_len, hidden_size]

        # Use mean pooling over sequence length
        pooled_output = embeddings.mean(dim=1)  # Shape: [batch_size, hidden_size]

        # Apply classification head
        logits = self.classification_head(pooled_output)

        return logits


class EnhancedProteinSequenceDataset(Dataset):
    """Enhanced dataset for protein sequences with ESMC tokenization."""

    def __init__(
        self,
        data_path: str,
        model,
        sequence_column: Optional[str] = None,
        label_column: str = "label",
        max_length: int = 1024,
    ):
        """
        Initialize the dataset.

        Args:
            data_path: Path to CSV file
            model: ESMC model object
            sequence_column: Name of sequence column (auto-detected if None)
            label_column: Name of label column
            max_length: Maximum sequence length for tokenization
        """
        self.data_path = data_path
        self.model = model
        self.max_length = max_length
        self.label_column = label_column

        # Load data
        self.df = pd.read_csv(data_path)
        logger.info(f"Loaded dataset with {len(self.df)} samples")

        # Auto-detect sequence column if not provided
        if sequence_column is None:
            sequence_column = self._auto_detect_sequence_column()
            logger.info(f"Auto-detected sequence column: {sequence_column}")

        self.sequence_column = sequence_column

        # Validate columns exist
        if self.sequence_column not in self.df.columns:
            raise ValueError(
                f"Sequence column '{self.sequence_column}' not found in data. "
                f"Available columns: {list(self.df.columns)}"
            )
        if self.label_column not in self.df.columns:
            raise ValueError(
                f"Label column '{self.label_column}' not found in data. "
                f"Available columns: {list(self.df.columns)}"
            )

        # Validate data
        self._validate_data()

    def _auto_detect_sequence_column(self) -> str:
        """Auto-detect the sequence column name."""
        available_columns = set(self.df.columns)

        # Priority order for sequence column detection
        priority_columns = ["sequence", "window", "protein_sequence", "seq"]

        for col in priority_columns:
            if col in available_columns:
                return col

        # Try to find any column that might contain sequences
        potential_columns = [
            col
            for col in available_columns
            if any(
                keyword in col.lower()
                for keyword in ["sequence", "seq", "window", "protein"]
            )
        ]

        if potential_columns:
            return potential_columns[0]

        raise ValueError(
            "Could not detect sequence column. Please specify --sequence-column. "
            "Expected columns: sequence, window, protein_sequence, seq, or similar"
        )

    def _validate_data(self):
        """Validate the dataset data."""
        # Check for missing values
        missing_sequences = self.df[self.sequence_column].isna().sum()
        missing_labels = self.df[self.label_column].isna().sum()

        if missing_sequences > 0:
            logger.warning(f"Found {missing_sequences} missing sequences")
        if missing_labels > 0:
            logger.warning(f"Found {missing_labels} missing labels")

        # Remove rows with missing data
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=[self.sequence_column, self.label_column])
        final_count = len(self.df)

        if initial_count != final_count:
            logger.info(f"Removed {initial_count - final_count} rows with missing data")

        # Validate sequence format (basic check)
        invalid_sequences = 0
        for seq in self.df[self.sequence_column]:
            if not isinstance(seq, str) or len(seq.strip()) == 0:
                invalid_sequences += 1

        if invalid_sequences > 0:
            logger.warning(f"Found {invalid_sequences} invalid sequences")
            self.df = self.df[self.df[self.sequence_column].str.strip().str.len() > 0]
            logger.info(f"Removed {invalid_sequences} invalid sequences")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        sequence = str(row[self.sequence_column]).strip()
        label = int(row[self.label_column])

        # Tokenize sequence using ESMC tokenizer
        encoded = self.model.tokenizer.encode_plus(sequence, return_tensors="pt")
        tokens = encoded["input_ids"].squeeze(0)  # Remove batch dimension

        # Truncate if necessary
        if tokens.size(0) > self.max_length:
            tokens = tokens[: self.max_length]

        # Ensure both tensors are on the same device
        device = tokens.device
        return {
            "input_ids": tokens,
            "labels": torch.tensor(label, dtype=torch.long, device=device),
        }


def get_frozen_embeddings(model, dataloader):
    """Extract frozen embeddings from the ESMC model."""
    embeddings = []
    labels = []

    model.eval()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Extracting embeddings"):
            input_ids = batch["input_ids"].to(DEVICE)
            batch_labels = batch["labels"].to(DEVICE)

            # Get embeddings from the model
            outputs = model(input_ids)

            # ESMC outputs embeddings with shape [batch_size, seq_len, hidden_size]
            embeddings_batch = (
                outputs.embeddings
            )  # Shape: [batch_size, seq_len, hidden_size]

            # Use mean pooling over sequence length
            pooled_output = embeddings_batch.mean(
                dim=1
            )  # Shape: [batch_size, hidden_size]

            embeddings.append(pooled_output.cpu().numpy())
            labels.append(batch_labels.cpu().numpy())

    return np.vstack(embeddings), np.concatenate(labels)


def create_dataset(
    batch_size=16,
    model_name=None,
    train_data_path=None,
    val_data_path=None,
    test_data_path=None,
    sequence_column=None,
    label_column="label",
):
    """
    Create datasets and dataloaders for training.

    Args:
        batch_size: Batch size for training
        model_name: ESMC model name
        train_data_path: Path to training data CSV
        val_data_path: Path to validation data CSV
        test_data_path: Path to test data CSV
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)

    Returns:
        Tuple of (train_loader, val_loader, test_loader, model)
    """
    if model_name is None:
        model_name = MODEL_NAME

    logger.info(f"Loading ESMC model: {model_name}")
    model = load_esmc_model(model_name)

    # Create datasets
    logger.info("\n--- Preparing Training DataLoader ---")
    train_df = pd.read_csv(train_data_path)
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    # Calculate weights for the WeightedRandomSampler to handle class imbalance
    class_counts = train_df[label_column].value_counts().sort_index()
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[label] for label in train_df[label_column]]
    sampler = WeightedRandomSampler(
        weights=sample_weights, num_samples=len(sample_weights), replacement=True
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler)
    logger.info("Training DataLoader created. It will use a weighted sampler.")

    # Create validation and test dataloaders
    logger.info("\n--- Preparing Validation & Test DataLoaders ---")
    val_dataset = EnhancedProteinSequenceDataset(
        val_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Validation samples: {len(val_dataset)}")
    logger.info(f"Test samples: {len(test_dataset)}")

    return train_loader, val_loader, test_loader, model


def train_baseline_model(
    batch_size=16,
    model_name=None,
    train_data_path=None,
    val_data_path=None,
    test_data_path=None,
    sequence_column=None,
    label_column="label",
):
    """
    Train a baseline model using frozen ESMC embeddings + XGBoost.

    Args:
        batch_size: Batch size for training
        model_name: ESMC model name
        train_data_path: Path to training data
        val_data_path: Path to validation data
        test_data_path: Path to test data
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)

    Returns:
        Dictionary containing baseline metrics
    """
    logger.info(f"Using device: {DEVICE}")

    if model_name is None:
        model_name = MODEL_NAME

    # Load Model
    logger.info(f"Loading model: {model_name}")
    model = load_esmc_model(model_name)

    # Create Datasets and Dataloaders
    logger.info("Loading data...")
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    val_dataset = EnhancedProteinSequenceDataset(
        val_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Generate Embeddings for all splits
    X_train, y_train = get_frozen_embeddings(model, train_loader)
    X_val, y_val = get_frozen_embeddings(model, val_loader)
    X_test, y_test = get_frozen_embeddings(model, test_loader)

    logger.info(f"Training embeddings shape: {X_train.shape}")
    logger.info(f"Validation embeddings shape: {X_val.shape}")
    logger.info(f"Test embeddings shape: {X_test.shape}")

    # Train XGBoost model
    logger.info("Training XGBoost baseline model...")
    import xgboost as xgb

    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
    )

    xgb_model.fit(X_train, y_train)

    # Evaluate on validation set
    val_pred_proba = xgb_model.predict_proba(X_val)[:, 1]
    val_pred = xgb_model.predict(X_val)

    val_auroc = roc_auc_score(y_val, val_pred_proba)
    val_auprc = average_precision_score(y_val, val_pred_proba)
    val_mcc = matthews_corrcoef(y_val, val_pred)

    logger.info(f"Validation AUROC: {val_auroc:.4f}")
    logger.info(f"Validation AUPRC: {val_auprc:.4f}")
    logger.info(f"Validation MCC: {val_mcc:.4f}")

    # Evaluate on test set
    test_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
    test_pred = xgb_model.predict(X_test)

    test_auroc = roc_auc_score(y_test, test_pred_proba)
    test_auprc = average_precision_score(y_test, test_pred_proba)
    test_mcc = matthews_corrcoef(y_test, test_pred)

    logger.info(f"Test AUROC: {test_auroc:.4f}")
    logger.info(f"Test AUPRC: {test_auprc:.4f}")
    logger.info(f"Test MCC: {test_mcc:.4f}")

    return {
        "validation": {
            "auroc": val_auroc,
            "auprc": val_auprc,
            "mcc": val_mcc,
        },
        "test": {
            "auroc": test_auroc,
            "auprc": test_auprc,
            "mcc": test_mcc,
        },
    }


def create_lora_path(lora_name: Optional[str] = None) -> tuple[str, str]:
    """
    Create a directory path for storing LoRA models.

    Args:
        lora_name: Custom name for the LoRA model. If None, generates a short UUID-based name.

    Returns:
        Tuple of (path_string, model_id_uuid) where:
        - path_string: Path string for the LoRA model directory
        - model_id_uuid: UUID string for the model ID (always a full UUID)

    Raises:
        ValueError: If a LoRA with the given name already exists
    """
    lora_base_path = get_lora_base_path("esmc")
    os.makedirs(lora_base_path, exist_ok=True)

    # Always generate a UUID for the model_id
    model_id_uuid = str(uuid4())

    if lora_name:
        # Validate the name (alphanumeric, hyphens, underscores only)
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", lora_name):
            raise ValueError(
                f"Invalid LoRA name '{lora_name}'. "
                "Name must contain only letters, numbers, hyphens, and underscores."
            )

        # Check for name conflicts
        named_path = os.path.join(lora_base_path, lora_name)
        if os.path.exists(named_path):
            raise ValueError(
                f"A LoRA model with name '{lora_name}' already exists at: {named_path}. "
                "Please choose a different name or remove the existing model."
            )

        os.makedirs(named_path, exist_ok=True)
        logger.info(f"Created LoRA directory: {named_path}")
        return named_path, model_id_uuid
    else:
        # Generate a short name based on UUID
        short_name = model_id_uuid[:8]
        path = os.path.join(lora_base_path, short_name)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created LoRA directory: {path}")
        return path, model_id_uuid


def train_lora(
    batch_size=8,
    num_epochs=5,
    learning_rate=1e-4,
    lora_r=8,
    lora_alpha=16,
    model_name=None,
    model_size=None,
    train_data_path=None,
    val_data_path=None,
    sequence_column=None,
    label_column="label",
    lora_name=None,
):
    """
    Train a LoRA fine-tuned model.

    Args:
        batch_size: Batch size for training
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        lora_r: LoRA rank
        lora_alpha: LoRA alpha
        model_name: ESMC model name
        model_size: Model size string
        train_data_path: Path to training data
        val_data_path: Path to validation data
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)
        lora_name: Custom name for the LoRA model

    Returns:
        Dictionary containing LoRA training metrics
    """
    if model_name is None:
        model_name = MODEL_NAME

    logger.info(
        f"Starting LoRA training with batch_size={batch_size}, num_epochs={num_epochs}, learning_rate={learning_rate}, lora_r={lora_r}, lora_alpha={lora_alpha}, model={model_name}"
    )

    if lora_name:
        logger.info(f"Using custom LoRA name: {lora_name}")

    lora_model_path, model_id_uuid = create_lora_path(lora_name)

    # Load model
    model = load_esmc_model(model_name)

    # Create classification model
    classifier_model = ESMCSequenceClassifier(model).to(DEVICE)

    train_df = pd.read_csv(train_data_path)
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    val_dataset = EnhancedProteinSequenceDataset(
        val_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    # Create the weighted sampler for the training set
    class_counts = train_df[label_column].value_counts().sort_index()
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[label] for label in train_df[label_column]]
    sampler = WeightedRandomSampler(
        weights=sample_weights, num_samples=len(sample_weights), replacement=True
    )

    logger.debug(
        f"Training samples: {len(train_df)}, Validation samples: {len(val_dataset)}"
    )
    logger.debug(f"Class distribution: {dict(class_counts)}")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # Optimizer and Scheduler
    optimizer = torch.optim.AdamW(classifier_model.parameters(), lr=learning_rate)
    num_training_steps = num_epochs * len(train_loader)
    logger.debug(f"Total training steps: {num_training_steps}")

    from transformers import get_scheduler

    lr_scheduler = get_scheduler(
        name="linear",
        optimizer=optimizer,
        num_warmup_steps=0,
        num_training_steps=num_training_steps,
    )

    # Metrics Setup
    val_metrics = {
        "AUROC": BinaryAUROC().to(DEVICE),
        "AUPRC": BinaryAveragePrecision().to(DEVICE),
        "MCC": BinaryMatthewsCorrCoef().to(DEVICE),
    }

    # Loss function
    criterion = nn.CrossEntropyLoss()

    # Training Loop
    best_auprc = 0
    for epoch in range(num_epochs):
        logger.info(f"\nEpoch {epoch + 1}/{num_epochs}")

        # Training phase
        classifier_model.train()
        train_loss = 0
        for batch in tqdm(train_loader, desc="Training"):
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            optimizer.zero_grad()
            logits = classifier_model(input_ids)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            lr_scheduler.step()

            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)
        logger.info(f"Average training loss: {avg_train_loss:.4f}")

        # Validation phase
        classifier_model.eval()
        val_loss = 0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                input_ids = batch["input_ids"].to(DEVICE)
                labels = batch["labels"].to(DEVICE)

                logits = classifier_model(input_ids)
                loss = criterion(logits, labels)

                val_loss += loss.item()
                all_preds.append(logits)
                all_labels.append(labels)

        avg_val_loss = val_loss / len(val_loader)
        logger.info(f"Average validation loss: {avg_val_loss:.4f}")

        # Calculate metrics
        all_preds = torch.cat(all_preds)
        all_labels = torch.cat(all_labels)

        # Convert logits to probabilities for binary classification
        # Binary metrics expect probabilities for the positive class
        pred_probs = torch.softmax(all_preds, dim=-1)[:, 1]

        for metric_name, metric in val_metrics.items():
            metric.update(pred_probs, all_labels)

        metrics_dict = {
            name: metric.compute().item() for name, metric in val_metrics.items()
        }
        logger.info(f"Validation metrics: {metrics_dict}")

        # Save best model
        if metrics_dict["AUPRC"] > best_auprc:
            best_auprc = metrics_dict["AUPRC"]
            logger.info(f"New best AUPRC: {best_auprc:.4f}")

            # Save model
            torch.save(
                classifier_model.state_dict(), os.path.join(lora_model_path, "model.pt")
            )

            # Save base model info
            torch.save(model, os.path.join(lora_model_path, "base_model.pt"))

            # Save training metadata
            metadata = {
                "model_name": model_name,
                "model_size": model_size,
                "training_config": {
                    "batch_size": batch_size,
                    "num_epochs": num_epochs,
                    "learning_rate": learning_rate,
                },
                "best_metrics": metrics_dict,
                "model_id": model_id_uuid,
                "created_at": datetime.now().isoformat(),
            }

            with open(
                os.path.join(lora_model_path, "training_metadata.json"), "w"
            ) as f:
                json.dump(metadata, f, indent=2)

        # Reset metrics for next epoch
        for metric in val_metrics.values():
            metric.reset()

    logger.info(f"Training completed. Best AUPRC: {best_auprc:.4f}")
    logger.info(f"Model saved to: {lora_model_path}")

    return {
        "best_auprc": best_auprc,
        "model_path": lora_model_path,
        "model_id": model_id_uuid,
    }


def run_final_eval(
    batch_size=16,
    model_path=None,
    model_name=None,
    test_data_path=None,
    sequence_column=None,
    label_column="label",
):
    """
    Run final evaluation on the test set.

    Args:
        batch_size: Batch size for evaluation
        model_path: Path to the trained model
        model_name: ESMC model name
        test_data_path: Path to test data
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)

    Returns:
        Dictionary containing final metrics
    """
    if model_name is None:
        model_name = MODEL_NAME

    logger.info(f"Starting final evaluation with batch_size={batch_size}")
    logger.info(f"Using device: {DEVICE}")

    # Load model
    model = load_esmc_model(model_name)

    # Load trained classifier
    classifier_model = ESMCSequenceClassifier(model).to(DEVICE)
    model_state_dict = torch.load(
        os.path.join(model_path, "model.pt"), map_location=DEVICE
    )
    classifier_model.load_state_dict(model_state_dict)

    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        model,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    logger.debug(f"Test dataset size: {len(test_dataset)}")

    metrics_collection = MetricCollection(
        {
            "AUROC": BinaryAUROC(),
            "AUPRC": BinaryAveragePrecision(),
            "MCC": BinaryMatthewsCorrCoef(),
        }
    ).to(DEVICE)

    classifier_model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            logits = classifier_model(input_ids)

            all_preds.append(logits)
            all_labels.append(labels)

    all_preds = torch.cat(all_preds)
    all_labels = torch.cat(all_labels)

    # Convert logits to probabilities for binary classification
    # Binary metrics expect probabilities for the positive class
    pred_probs = torch.softmax(all_preds, dim=-1)[:, 1]

    final_metrics = metrics_collection(pred_probs, all_labels)
    final_metrics_dict = {name: metric.item() for name, metric in final_metrics.items()}

    logger.info("Final evaluation results:")
    for metric_name, metric_value in final_metrics_dict.items():
        logger.info(f"{metric_name}: {metric_value:.4f}")

    return final_metrics_dict


def run_full_pipeline(
    baseline_batch_size=16,
    lora_batch_size=8,
    num_epochs=5,
    learning_rate=1e-4,
    lora_r=8,
    lora_alpha=16,
    model_size="300m",
    train_baseline=True,
    train_data_path=None,
    val_data_path=None,
    test_data_path=None,
    features=None,
    lora_name=None,
):
    """
    Run the full training pipeline including baseline and LoRA training.

    Args:
        baseline_batch_size: Batch size for baseline training
        lora_batch_size: Batch size for LoRA training
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        lora_r: LoRA rank
        lora_alpha: LoRA alpha
        model_size: Model size ("300m", "600m")
        train_baseline: Whether to train baseline model
        train_data_path: Path to training data CSV
        val_data_path: Path to validation data CSV
        test_data_path: Path to test data CSV
        features: Dictionary mapping feature names to column names (e.g., {"sequence": "window", "label": "target"})
        lora_name: Custom name for the LoRA model

    Returns:
        Dictionary containing training results and metrics
    """
    # Use default features if none provided
    if features is None:
        features = {"sequence": None, "label": "label"}

    # Extract column names from features
    sequence_column = features.get("sequence")
    label_column = features.get("label", "label")

    model_name = get_model_name(model_size)

    start_time = datetime.now()
    start_timestamp = start_time.isoformat()

    logger.info("=" * 60)
    logger.info("STARTING COMPLETE ESMC TRAINING PIPELINE")
    logger.info(f"Model: {model_name} ({model_size})")
    logger.info(f"Start time: {start_timestamp}")
    logger.info("=" * 60)

    # Step 1: Create dataset
    logger.info("\nSTEP 1: Creating dataset...")
    create_dataset(
        batch_size=baseline_batch_size,
        model_name=model_name,
        train_data_path=train_data_path,
        val_data_path=val_data_path,
        test_data_path=test_data_path,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    # Step 2: Train baseline model (optional)
    baseline_results = None
    if train_baseline:
        logger.info("\nSTEP 2: Training baseline model...")
        baseline_results = train_baseline_model(
            batch_size=baseline_batch_size,
            model_name=model_name,
            train_data_path=train_data_path,
            val_data_path=val_data_path,
            test_data_path=test_data_path,
            sequence_column=sequence_column,
            label_column=label_column,
        )
        logger.info("Baseline training completed.")

    # Step 3: Train LoRA model
    logger.info("\nSTEP 3: Training LoRA model...")
    lora_results = train_lora(
        batch_size=lora_batch_size,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        lora_r=lora_r,
        lora_alpha=lora_alpha,
        model_name=model_name,
        model_size=model_size,
        train_data_path=train_data_path,
        val_data_path=val_data_path,
        sequence_column=sequence_column,
        label_column=label_column,
        lora_name=lora_name,
    )
    logger.info("LoRA training completed.")

    # Step 4: Final evaluation
    logger.info("\nSTEP 4: Running final evaluation...")
    final_results = run_final_eval(
        batch_size=baseline_batch_size,
        model_path=lora_results["model_path"],
        model_name=model_name,
        test_data_path=test_data_path,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    logger.info("Final evaluation completed.")

    # Compile results
    end_time = datetime.now()
    end_timestamp = end_time.isoformat()
    total_time = (end_time - start_time).total_seconds()

    results = {
        "model_name": model_name,
        "model_size": model_size,
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "total_time_seconds": total_time,
        "lora_results": lora_results,
        "final_evaluation": final_results,
    }

    if baseline_results:
        results["baseline_results"] = baseline_results

    logger.info("=" * 60)
    logger.info("TRAINING PIPELINE COMPLETED")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info("=" * 60)

    return results
