from pydantic import BaseModel
from uuid import uuid4
import pandas as pd
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from peft import LoraConfig, get_peft_model, TaskType
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import xgboost as xgb
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
from peft import PeftModel
from transformers import get_scheduler
import json
from typing import Optional, Dict

from vaultide.config import get_lora_base_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vaultide")

MODEL_NAME = "facebook/esm2_t33_650M_UR50D"
# Use CUDA if available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Model size mapping
MODEL_SIZE_MAPPING = {
    # ESM-2 model variants
    "8m": "facebook/esm2_t6_8M_UR50D",
    "35m": "facebook/esm2_t12_35M_UR50D",
    "150m": "facebook/esm2_t30_150M_UR50D",
    "650m": "facebook/esm2_t33_650M_UR50D",
    "3b": "facebook/esm2_t36_3B_UR50D",
    "15b": "facebook/esm2_t48_15B_UR50D",
}


def get_model_name(model_size: str) -> str:
    """
    Get the model name based on the model size.

    Args:
        model_size: One of "8m", "35m", "150m", "650m", "3b", "15b"

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


class Esm2TrainingInput(BaseModel):
    baseline_batch_size: int = 16
    lora_batch_size: int = 8
    num_epochs: int = 5
    lora_r: int = 8
    lora_alpha: int = 16
    learning_rate: float = 1e-4
    model_size: str = "650m"
    train_baseline: bool = True
    # Data paths - these will be task-specific
    train_data_path: str
    val_data_path: str
    test_data_path: str
    # Feature mappings - validated by the CLI
    features: Dict[str, str] = {}  # Maps feature names to column names


class Esm2TrainingOutput(BaseModel):
    result: str
    baseline_metrics: dict | None
    lora_metrics: dict
    final_metrics: dict
    training_summary: dict
    model_paths: dict


class EnhancedProteinSequenceDataset(Dataset):
    """
    PyTorch Dataset for protein sequence classification using ESM-2.
    Supports configurable sequence and label column names.
    """

    def __init__(
        self,
        csv_file,
        tokenizer,
        sequence_column=None,
        label_column="label",
        max_length=35,
    ):
        self.data = pd.read_csv(csv_file)
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Auto-detect sequence column with sensible defaults
        if sequence_column is not None:
            self.sequence_column = sequence_column
        elif "sequence" in self.data.columns:
            self.sequence_column = "sequence"
        elif "window" in self.data.columns:
            self.sequence_column = "window"
            logger.info("Detected PTM prediction format (using 'window' column)")
        elif "protein_sequence" in self.data.columns:
            self.sequence_column = "protein_sequence"
        elif "seq" in self.data.columns:
            self.sequence_column = "seq"
        else:
            # Try to find any column that might contain sequences
            potential_columns = [
                col
                for col in self.data.columns
                if any(
                    keyword in col.lower()
                    for keyword in ["sequence", "seq", "window", "protein"]
                )
            ]
            if potential_columns:
                self.sequence_column = potential_columns[0]
                logger.info(f"Auto-detected sequence column: {self.sequence_column}")
            else:
                raise ValueError(
                    "Could not detect sequence column. Please specify --sequence-column. "
                    "Expected columns: sequence, window, protein_sequence, seq, or similar"
                )

        # Validate sequence column exists
        if self.sequence_column not in self.data.columns:
            raise ValueError(
                f"Sequence column '{self.sequence_column}' not found in data. "
                f"Available columns: {list(self.data.columns)}"
            )

        # Auto-detect label column with sensible defaults
        if label_column is not None:
            self.label_column = label_column
        elif "label" in self.data.columns:
            self.label_column = "label"
        elif "target" in self.data.columns:
            self.label_column = "target"
        elif "class" in self.data.columns:
            self.label_column = "class"
        else:
            # Try to find any column that might contain labels
            potential_columns = [
                col
                for col in self.data.columns
                if any(
                    keyword in col.lower()
                    for keyword in ["label", "target", "class", "y"]
                )
            ]
            if potential_columns:
                self.label_column = potential_columns[0]
                logger.info(f"Auto-detected label column: {self.label_column}")
            else:
                raise ValueError(
                    "Could not detect label column. Please specify --label-column. "
                    "Expected columns: label, target, class, or similar"
                )

        # Validate label column exists
        if self.label_column not in self.data.columns:
            raise ValueError(
                f"Label column '{self.label_column}' not found in data. "
                f"Available columns: {list(self.data.columns)}"
            )

        logger.info(f"Using sequence column: {self.sequence_column}")
        logger.info(f"Using label column: {self.label_column}")
        logger.info(f"Dataset size: {len(self.data)} samples")

        # Validate that sequences are strings
        non_string_sequences = (
            self.data[self.sequence_column]
            .apply(lambda x: not isinstance(x, str))
            .sum()
        )
        if non_string_sequences > 0:
            logger.warning(
                f"Found {non_string_sequences} non-string sequences. Converting to string."
            )
            self.data[self.sequence_column] = self.data[self.sequence_column].astype(
                str
            )

        # Validate that labels are numeric
        try:
            self.data[self.label_column] = pd.to_numeric(self.data[self.label_column])
        except ValueError:
            raise ValueError(
                f"Label column '{self.label_column}' contains non-numeric values. "
                f"Labels must be numeric (0, 1 for binary classification)."
            )

    def __len__(self):
        """Returns the total number of samples in the dataset."""
        return len(self.data)

    def _extract_sequence_features(self, sequence):
        """Extract sequence-based features."""
        features = {}

        # Tokenize the sequence
        tokenized_output = self.tokenizer(
            sequence,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        features["input_ids"] = tokenized_output["input_ids"].squeeze()
        features["attention_mask"] = tokenized_output["attention_mask"].squeeze()

        return features

    def __getitem__(self, idx):
        """
        Fetches one sample from the dataset at the given index.
        Returns a dictionary with sequence features and labels.
        """
        row = self.data.iloc[idx]
        sequence = row[self.sequence_column]
        label = row[self.label_column]

        # Extract sequence features
        features = self._extract_sequence_features(sequence)

        # Add labels
        features["labels"] = torch.tensor(label, dtype=torch.long)

        return features


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
        model_name: ESM-2 model name
        train_data_path: Path to training data CSV
        val_data_path: Path to validation data CSV
        test_data_path: Path to test data CSV
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)

    Returns:
        Tuple of (train_loader, val_loader, test_loader, tokenizer)
    """
    if model_name is None:
        model_name = MODEL_NAME

    logger.info(f"Loading tokenizer for model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Create datasets
    logger.info("\n--- Preparing Training DataLoader ---")
    train_df = pd.read_csv(train_data_path)
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        tokenizer,
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
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    logger.info("Validation and Test DataLoaders created.")

    # Inspect a batch to verify everything works
    logger.info("\n--- Inspecting one batch from the Training DataLoader ---")
    batch = next(iter(train_loader))

    logger.info(f"Keys in the batch: {batch.keys()}")
    logger.info(f"Shape of input_ids: {batch['input_ids'].shape}")
    logger.info(f"Shape of attention_mask: {batch['attention_mask'].shape}")
    logger.info(f"Shape of labels: {batch['labels'].shape}")
    logger.info("Example labels in the batch (should be a mix of 0s and 1s):")
    logger.info(f"{batch['labels']}")

    return train_loader, val_loader, test_loader, tokenizer


def get_frozen_embeddings(model, dataloader):
    """
    Passes data through the frozen ESM-2 model and extracts embeddings.
    We will use the embedding of the [CLS] token as a representation of the whole sequence.
    """
    model.eval()

    all_embeddings = []
    all_labels = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Generating Embeddings"):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"]

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            last_hidden_state = outputs.last_hidden_state

            # The [CLS] token is always at the first position (index 0)
            # Its embedding is a good summary of the entire sequence.
            cls_embeddings = last_hidden_state[:, 0, :]

            all_embeddings.append(cls_embeddings.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    return np.concatenate(all_embeddings), np.concatenate(all_labels)


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
    Train a baseline model using frozen ESM-2 embeddings + XGBoost.

    Args:
        batch_size: Batch size for training
        model_name: ESM-2 model name
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

    # Load Model and Tokenizer
    logger.info(f"Loading model and tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(DEVICE)

    # Create Datasets and Dataloaders
    logger.info("Loading data...")
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    val_dataset = EnhancedProteinSequenceDataset(
        val_data_path,
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        tokenizer,
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

    logger.info(f"\nShape of training embeddings: {X_train.shape}")
    logger.info(f"Shape of training labels: {y_train.shape}")

    # Train XGBoost Classifier
    logger.info("\nTraining XGBoost classifier...")
    scale_pos_weight = np.sum(y_train == 0) / np.sum(y_train == 1)
    logger.debug(f"Class imbalance scale_pos_weight: {scale_pos_weight:.4f}")

    xgb_classifier = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        scale_pos_weight=scale_pos_weight,
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        early_stopping_rounds=10,
    )

    xgb_classifier.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    logger.info("XGBoost training complete.")

    # Evaluate on the Test Set
    logger.info("\n--- Evaluating on the Test Set ---")
    y_pred_proba = xgb_classifier.predict_proba(X_test)[:, 1]
    y_pred_labels = xgb_classifier.predict(X_test)

    auroc = roc_auc_score(y_test, y_pred_proba)
    auprc = average_precision_score(y_test, y_pred_proba)
    mcc = matthews_corrcoef(y_test, y_pred_labels)

    logger.info("\n--- Baseline Model Performance (Frozen ESM-2 + XGBoost) ---")
    logger.info(f"Test Set AUROC: {auroc:.4f}")
    logger.info(f"Test Set AUPRC: {auprc:.4f}")
    logger.info(f"Test Set MCC:   {mcc:.4f}")
    logger.info("------------------------------------------------------------")
    logger.info("\nThese are your benchmark scores to beat with LoRA fine-tuning.")

    if auroc < 0.6:
        logger.warning(
            f"Baseline AUROC ({auroc:.4f}) is below 0.6 - consider data quality or model selection"
        )
    if auprc < 0.2:
        logger.warning(
            f"Baseline AUPRC ({auprc:.4f}) is below 0.2 - consider class imbalance handling"
        )

    baseline_metrics = {
        "auroc": float(auroc),
        "auprc": float(auprc),
        "mcc": float(mcc),
        "test_samples": len(y_test),
        "positive_samples": int(np.sum(y_test == 1)),
        "negative_samples": int(np.sum(y_test == 0)),
    }

    return baseline_metrics


def train_one_epoch(model, dataloader, optimizer, lr_scheduler):
    """Train the model for one epoch."""
    model.train()
    total_loss = 0
    for batch in tqdm(dataloader, desc="Training"):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss

        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def evaluate(model, dataloader, metrics_collection):
    """
    Evaluates the model on a given dataset and computes metrics.
    """
    model.eval()
    for metric in metrics_collection.values():
        metric.reset()

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            outputs = model(**batch)

            preds = torch.softmax(outputs.logits, dim=-1)[:, 1]
            labels = batch["labels"].int()

            for metric in metrics_collection.values():
                metric.update(preds, labels)

    results = {name: metric.compute() for name, metric in metrics_collection.items()}
    return results


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
    lora_base_path = get_lora_base_path("esm2")
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
        logger.info(f"Created LoRA directory with custom name: {named_path}")
        return named_path, model_id_uuid
    else:
        # Generate short UUID-based name for directory (first section only)
        unique_id = str(uuid4()).split("-")[0]  # 8 hex chars
        unique_path = os.path.join(lora_base_path, unique_id)
        # Ensure no collision (very unlikely, but check)
        while os.path.exists(unique_path):
            unique_id = str(uuid4()).split("-")[0]
            unique_path = os.path.join(lora_base_path, unique_id)
        os.makedirs(unique_path, exist_ok=True)
        logger.info(f"Created LoRA directory with auto-generated name: {unique_path}")
        return unique_path, model_id_uuid


def create_unique_lora_path() -> str:
    """
    Create a unique directory path for storing LoRA models.
    (Backward compatibility function)

    Returns:
        Unique path string for the LoRA model directory
    """
    path, _ = create_lora_path()
    return path


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
        model_name: ESM-2 model name
        model_size: Model size string
        train_data_path: Path to training data
        val_data_path: Path to validation data
        sequence_column: Name of sequence column in CSV (auto-detected if None)
        label_column: Name of label column in CSV (default: label)

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

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_df = pd.read_csv(train_data_path)
    train_dataset = EnhancedProteinSequenceDataset(
        train_data_path,
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    val_dataset = EnhancedProteinSequenceDataset(
        val_data_path,
        tokenizer,
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

    # Load Model and Apply PEFT
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )

    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.1,
        target_modules=["query", "key", "value"],
    )

    model = get_peft_model(model, lora_config).to(DEVICE)
    logger.info("\nModel with LoRA layers:")
    model.print_trainable_parameters()

    # Optimizer and Scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    num_training_steps = num_epochs * len(train_loader)
    logger.debug(f"Total training steps: {num_training_steps}")
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

    # Training Loop
    best_auprc = 0
    training_history = []

    for epoch in range(num_epochs):
        logger.info(f"\n--- Epoch {epoch+1}/{num_epochs} ---")
        avg_train_loss = train_one_epoch(model, train_loader, optimizer, lr_scheduler)
        logger.info(f"Average Training Loss: {avg_train_loss:.4f}")

        metrics_collection = torch.nn.ModuleDict(val_metrics).to(DEVICE)
        results = evaluate(model, val_loader, metrics_collection)

        logger.info("Validation Metrics:")
        val_auroc = results["AUROC"].item()
        val_auprc = results["AUPRC"].item()
        val_mcc = results["MCC"].item()
        logger.info(f"  AUROC: {val_auroc:.4f}")
        logger.info(f"  AUPRC: {val_auprc:.4f}")
        logger.info(f"  MCC:   {val_mcc:.4f}")

        epoch_result = {
            "epoch": epoch + 1,
            "train_loss": avg_train_loss,
            "val_auroc": val_auroc,
            "val_auprc": val_auprc,
            "val_mcc": val_mcc,
        }
        training_history.append(epoch_result)

        if val_auprc > best_auprc:
            best_auprc = val_auprc
            logger.info("New best model found! Saving...")
            model.save_pretrained(lora_model_path)

            # Save additional metadata including model_id
            adapter_config_path = os.path.join(lora_model_path, "adapter_config.json")
            if os.path.exists(adapter_config_path):
                try:
                    with open(adapter_config_path, "r") as f:
                        config = json.load(f)

                    # Add model_id to the config
                    config["model_id"] = model_id_uuid

                    with open(adapter_config_path, "w") as f:
                        json.dump(config, f, indent=2)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(
                        f"Could not update adapter_config.json with model_id: {e}"
                    )
        else:
            logger.debug(
                f"No improvement in AUPRC. Best: {best_auprc:.4f}, Current: {val_auprc:.4f}"
            )

    logger.info("\n--- Training Complete ---")
    logger.info(f"Best validation AUPRC achieved: {best_auprc:.4f}")
    logger.info(f"Best model saved to directory: '{lora_model_path}")

    lora_metrics = {
        "best_val_auprc": float(best_auprc),
        "final_val_auroc": float(val_auroc),
        "final_val_auprc": float(val_auprc),
        "final_val_mcc": float(val_mcc),
        "training_history": training_history,
        "num_epochs": num_epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
        "model_size": model_size,
        "model_name": model_name,
        "model_path": lora_model_path,
        "model_id": model_id_uuid,
    }

    return lora_metrics


def evaluate_final_model(model, dataloader, metrics_collection):
    """
    Evaluates the final model on the test set.
    """
    model.eval()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating on Test Set"):
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            outputs = model(**batch)

            preds = torch.softmax(outputs.logits, dim=-1)[:, 1]
            metrics_collection.update(preds, batch["labels"].int())

    return metrics_collection.compute()


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
        model_path: Path to the trained LoRA model
        model_name: ESM-2 model name
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

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    test_dataset = EnhancedProteinSequenceDataset(
        test_data_path,
        tokenizer,
        sequence_column=sequence_column,
        label_column=label_column,
    )
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    logger.debug(f"Test dataset size: {len(test_dataset)}")

    logger.info(f"Loading the base model: {model_name}")
    base_model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )

    if model_path is None:
        logger.error("No model path provided for final evaluation")
        raise ValueError("model_path must be provided for final evaluation")

    logger.info(f"Loading the LoRA adapter from: {model_path}")
    model = PeftModel.from_pretrained(base_model, model_path).to(DEVICE)
    logger.info("Successfully loaded fine-tuned model.")

    metrics_collection = MetricCollection(
        {
            "AUROC": BinaryAUROC(),
            "AUPRC": BinaryAveragePrecision(),
            "MCC": BinaryMatthewsCorrCoef(),
        }
    ).to(DEVICE)

    final_metrics = evaluate_final_model(model, test_loader, metrics_collection)

    auroc = final_metrics["AUROC"].item()
    auprc = final_metrics["AUPRC"].item()
    mcc = final_metrics["MCC"].item()

    logger.info("\n" + "=" * 50)
    logger.info("---      Final LoRA Model Performance on TEST SET      ---")
    logger.info("=" * 50)
    logger.info(f"Test Set AUROC: {auroc:.4f}")
    logger.info(f"Test Set AUPRC: {auprc:.4f}")
    logger.info(f"Test Set MCC:   {mcc:.4f}")
    logger.info("=" * 50)
    logger.info("\nThese are the final, publishable results for your model.")

    if auroc > 0.8:
        logger.info("Excellent AUROC performance (>0.8)")
    elif auroc > 0.7:
        logger.info("Good AUROC performance (>0.7)")
    elif auroc > 0.6:
        logger.info("Acceptable AUROC performance (>0.6)")
    else:
        logger.warning("Poor AUROC performance (<0.6) - consider model improvements")

    if auprc > 0.5:
        logger.info("Excellent AUPRC performance (>0.5)")
    elif auprc > 0.3:
        logger.info("Good AUPRC performance (>0.3)")
    elif auprc > 0.2:
        logger.info("Acceptable AUPRC performance (>0.2)")
    else:
        logger.warning(
            "Poor AUPRC performance (<0.2) - consider class imbalance handling"
        )

    final_metrics_dict = {
        "auroc": float(auroc),
        "auprc": float(auprc),
        "mcc": float(mcc),
        "test_samples": len(test_dataset),
        "model_path": model_path,
        "performance_analysis": {
            "auroc_level": "excellent"
            if auroc > 0.8
            else "good"
            if auroc > 0.7
            else "acceptable"
            if auroc > 0.6
            else "poor",
            "auprc_level": "excellent"
            if auprc > 0.5
            else "good"
            if auprc > 0.3
            else "acceptable"
            if auprc > 0.2
            else "poor",
        },
    }

    return final_metrics_dict


def run_full_pipeline(
    baseline_batch_size=16,
    lora_batch_size=8,
    num_epochs=5,
    learning_rate=1e-4,
    lora_r=8,
    lora_alpha=16,
    model_size="650m",
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
        model_size: Model size ("8m", "35m", "150m", "650m", "3b", "15b")
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
    logger.info("STARTING COMPLETE ESM-2 TRAINING PIPELINE")
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

    baseline_metrics = None
    if train_baseline:
        logger.info("\nSTEP 2: Training baseline model...")
        baseline_metrics = train_baseline_model(
            batch_size=baseline_batch_size,
            model_name=model_name,
            train_data_path=train_data_path,
            val_data_path=val_data_path,
            test_data_path=test_data_path,
            sequence_column=sequence_column,
            label_column=label_column,
        )
    else:
        logger.info("\nSTEP 2: Skipping baseline training as requested...")

    # Step 3: Train LoRA model
    logger.info("\nSTEP 3: Training LoRA model...")
    lora_metrics = train_lora(
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

    # Step 4: Final evaluation
    logger.info("\nSTEP 4: Running final evaluation...")
    final_metrics = run_final_eval(
        batch_size=baseline_batch_size,
        model_path=lora_metrics["model_path"],
        model_name=model_name,
        test_data_path=test_data_path,
        sequence_column=sequence_column,
        label_column=label_column,
    )

    # Create training summary
    training_summary = {
        "pipeline_completed": True,
        "training_parameters": {
            "baseline_batch_size": baseline_batch_size,
            "lora_batch_size": lora_batch_size,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
            "lora_r": lora_r,
            "lora_alpha": lora_alpha,
            "model_size": model_size,
            "model_name": model_name,
            "train_baseline": train_baseline,
        },
        "model_paths": {"lora_model_path": lora_metrics["model_path"]},
        "features": features,
    }

    if baseline_metrics:
        training_summary["baseline_improvement"] = {
            "auroc_improvement": final_metrics["auroc"] - baseline_metrics["auroc"],
            "auprc_improvement": final_metrics["auprc"] - baseline_metrics["auprc"],
            "mcc_improvement": final_metrics["mcc"] - baseline_metrics["mcc"],
        }
        training_summary["best_performance"] = {
            "auroc": max(baseline_metrics["auroc"], final_metrics["auroc"]),
            "auprc": max(baseline_metrics["auprc"], final_metrics["auprc"]),
            "mcc": max(baseline_metrics["mcc"], final_metrics["mcc"]),
        }
    else:
        training_summary["best_performance"] = {
            "auroc": final_metrics["auroc"],
            "auprc": final_metrics["auprc"],
            "mcc": final_metrics["mcc"],
        }

    end_time = datetime.now()
    end_timestamp = end_time.isoformat()
    duration = end_time - start_time

    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"End time: {end_timestamp}")
    logger.info(f"Total duration: {duration}")
    logger.info("=" * 60)

    training_summary["timestamps"] = {
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "duration_seconds": duration.total_seconds(),
        "duration_human": str(duration),
    }

    return {
        "baseline_metrics": baseline_metrics,
        "lora_metrics": lora_metrics,
        "final_metrics": final_metrics,
        "training_summary": training_summary,
    }
