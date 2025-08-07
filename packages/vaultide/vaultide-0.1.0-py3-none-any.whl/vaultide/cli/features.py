"""
Feature validation utilities for Vaultide CLI.

This module provides feature validation classes for different model types,
allowing each model to define its own required and optional features.
"""

import logging
from typing import Dict, Set

from .security import SecurityError, PathValidator

logger = logging.getLogger("vaultide")


class FeatureValidator:
    """Base class for feature validation that each model type can extend."""

    def __init__(self, model_type: str):
        self.model_type = model_type
        self.required_features: Set[str] = set()
        self.optional_features: Set[str] = set()
        self.feature_descriptions: Dict[str, str] = {}

    def validate_features(
        self, data_path: str, features: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Validate that required features are present in the dataset.

        Args:
            data_path: Path to the CSV file
            features: Dictionary mapping feature names to column names

        Returns:
            Dictionary of validated feature mappings

        Raises:
            ValueError: If required features are missing or invalid
            SecurityError: If file path is unsafe
        """
        import pandas as pd

        # Validate the data path for security
        try:
            PathValidator.is_safe_path(data_path)
        except SecurityError as e:
            raise ValueError(f"Invalid data file path: {e}")

        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            raise ValueError(f"Could not read CSV file {data_path}: {e}")

        available_columns = set(df.columns)
        validated_features = {}

        # Validate required features
        for feature in self.required_features:
            if feature not in features:
                raise ValueError(
                    f"Required feature '{feature}' not specified for {self.model_type}"
                )

            column_name = features[feature]
            if column_name not in available_columns:
                raise ValueError(
                    f"Column '{column_name}' for feature '{feature}' not found in {data_path}. "
                    f"Available columns: {list(available_columns)}"
                )
            validated_features[feature] = column_name

        # Validate optional features
        for feature in self.optional_features:
            if feature in features:
                column_name = features[feature]
                if column_name not in available_columns:
                    raise ValueError(
                        f"Column '{column_name}' for feature '{feature}' not found in {data_path}. "
                        f"Available columns: {list(available_columns)}"
                    )
                validated_features[feature] = column_name

        return validated_features

    def get_feature_help(self) -> str:
        """Get help text for the model's features."""
        help_lines = [f"Features for {self.model_type} model:"]

        if self.required_features:
            help_lines.append("  Required features:")
            for feature in sorted(self.required_features):
                desc = self.feature_descriptions.get(
                    feature, "No description available"
                )
                help_lines.append(f"    {feature}: {desc}")

        if self.optional_features:
            help_lines.append("  Optional features:")
            for feature in sorted(self.optional_features):
                desc = self.feature_descriptions.get(
                    feature, "No description available"
                )
                help_lines.append(f"    {feature}: {desc}")

        return "\n".join(help_lines)


class Esm2FeatureValidator(FeatureValidator):
    """Feature validator for ESM-2 models."""

    def __init__(self):
        super().__init__("esm2")
        self.required_features = {"sequence", "label"}
        self.optional_features = set()
        self.feature_descriptions = {
            "sequence": "Protein sequence column (auto-detected if not specified)",
            "label": "Target label column for classification (default: label)",
        }

    def validate_features(
        self, data_path: str, features: Dict[str, str]
    ) -> Dict[str, str]:
        """ESM-2 specific feature validation with auto-detection."""
        import pandas as pd

        # Validate the data path for security
        try:
            PathValidator.is_safe_path(data_path)
        except SecurityError as e:
            raise ValueError(f"Invalid data file path: {e}")

        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            raise ValueError(f"Could not read CSV file {data_path}: {e}")

        available_columns = set(df.columns)
        validated_features = {}

        # Auto-detect sequence column if not specified
        sequence_column = features.get("sequence")
        if sequence_column is None:
            # Auto-detection logic
            if "sequence" in available_columns:
                sequence_column = "sequence"
            elif "window" in available_columns:
                sequence_column = "window"
                logger.info("Detected PTM prediction format (using 'window' column)")
            elif "protein_sequence" in available_columns:
                sequence_column = "protein_sequence"
            elif "seq" in available_columns:
                sequence_column = "seq"
            else:
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
                    sequence_column = potential_columns[0]
                    logger.info(f"Auto-detected sequence column: {sequence_column}")
                else:
                    raise ValueError(
                        "Could not detect sequence column. Please specify --sequence-column. "
                        "Expected columns: sequence, window, protein_sequence, seq, or similar"
                    )

        if sequence_column not in available_columns:
            raise ValueError(
                f"Sequence column '{sequence_column}' not found in data. "
                f"Available columns: {list(available_columns)}"
            )
        validated_features["sequence"] = sequence_column

        # Auto-detect label column if not specified
        label_column = features.get("label", "label")
        if label_column not in available_columns:
            # Try common label column names
            for common_name in ["label", "target", "class"]:
                if common_name in available_columns:
                    label_column = common_name
                    logger.info(f"Auto-detected label column: {label_column}")
                    break
            else:
                # Try to find any column that might contain labels
                potential_columns = [
                    col
                    for col in available_columns
                    if any(
                        keyword in col.lower()
                        for keyword in ["label", "target", "class", "y"]
                    )
                ]
                if potential_columns:
                    label_column = potential_columns[0]
                    logger.info(f"Auto-detected label column: {label_column}")
                else:
                    raise ValueError(
                        f"Label column '{label_column}' not found in data. "
                        f"Available columns: {list(available_columns)}"
                    )

        validated_features["label"] = label_column

        logger.info(f"Using sequence column: {sequence_column}")
        logger.info(f"Using label column: {label_column}")

        return validated_features


class EsmcFeatureValidator(FeatureValidator):
    """Feature validator for ESMC models."""

    def __init__(self):
        super().__init__("esmc")
        self.required_features = {"sequence", "label"}
        self.optional_features = set()
        self.feature_descriptions = {
            "sequence": "Protein sequence column (auto-detected if not specified)",
            "label": "Target label column for classification (default: label)",
        }

    def validate_features(
        self, data_path: str, features: Dict[str, str]
    ) -> Dict[str, str]:
        """ESMC specific feature validation with auto-detection."""
        import pandas as pd

        # Validate the data path for security
        try:
            PathValidator.is_safe_path(data_path)
        except SecurityError as e:
            raise ValueError(f"Invalid data file path: {e}")

        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            raise ValueError(f"Could not read CSV file {data_path}: {e}")

        available_columns = set(df.columns)
        validated_features = {}

        # Auto-detect sequence column if not specified
        sequence_column = features.get("sequence")
        if sequence_column is None:
            # Auto-detection logic
            if "sequence" in available_columns:
                sequence_column = "sequence"
            elif "window" in available_columns:
                sequence_column = "window"
                logger.info("Detected PTM prediction format (using 'window' column)")
            elif "protein_sequence" in available_columns:
                sequence_column = "protein_sequence"
            elif "seq" in available_columns:
                sequence_column = "seq"
            else:
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
                    sequence_column = potential_columns[0]
                    logger.info(f"Auto-detected sequence column: {sequence_column}")
                else:
                    raise ValueError(
                        "Could not detect sequence column. Please specify --sequence-column. "
                        "Expected columns: sequence, window, protein_sequence, seq, or similar"
                    )

        if sequence_column not in available_columns:
            raise ValueError(
                f"Sequence column '{sequence_column}' not found in data. "
                f"Available columns: {list(available_columns)}"
            )
        validated_features["sequence"] = sequence_column

        # Auto-detect label column if not specified
        label_column = features.get("label", "label")
        if label_column not in available_columns:
            # Try common label column names
            for common_name in ["label", "target", "class"]:
                if common_name in available_columns:
                    label_column = common_name
                    logger.info(f"Auto-detected label column: {label_column}")
                    break
            else:
                # Try to find any column that might contain labels
                potential_columns = [
                    col
                    for col in available_columns
                    if any(
                        keyword in col.lower()
                        for keyword in ["label", "target", "class", "y"]
                    )
                ]
                if potential_columns:
                    label_column = potential_columns[0]
                    logger.info(f"Auto-detected label column: {label_column}")
                else:
                    raise ValueError(
                        f"Label column '{label_column}' not found in data. "
                        f"Available columns: {list(available_columns)}"
                    )

        validated_features["label"] = label_column

        logger.info(f"Using sequence column: {sequence_column}")
        logger.info(f"Using label column: {label_column}")

        return validated_features


# Feature validator registry
FEATURE_VALIDATORS = {
    "esm2": Esm2FeatureValidator(),
    "esmc": EsmcFeatureValidator(),
}
