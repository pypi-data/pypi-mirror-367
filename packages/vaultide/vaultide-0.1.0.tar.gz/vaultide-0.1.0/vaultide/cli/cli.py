"""
Main CLI class for Vaultide.

This module contains the VaultideCLI class which handles all CLI operations
including training, prediction, listing, and serving models.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from .security import SecurityError, PathValidator, ModelValidator, SecureFileHandler
from .features import FEATURE_VALIDATORS
from vaultide.config import (
    get_config_path,
    get_lora_base_path,
    ensure_directories,
    DEFAULT_LORA_BASE,
)

logger = logging.getLogger("vaultide")


class VaultideCLI:
    """Main CLI class for Vaultide."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the CLI with optional config path."""
        self.config_path = config_path or get_config_path()

        # Expand tilde in config path if present
        if self.config_path and "~" in self.config_path:
            self.config_path = os.path.expanduser(self.config_path)

        # Validate the config path for security
        try:
            PathValidator.is_safe_path(self.config_path)
        except SecurityError as e:
            raise SecurityError(f"Invalid config path: {e}")

        self.config = self.load_config()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        ensure_directories()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                import yaml

                # Validate the config path
                PathValidator.is_safe_path(self.config_path)
                with SecureFileHandler.safe_open(self.config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except SecurityError as e:
                logger.error(f"Security error loading config: {e}")
                return {}
            except Exception as e:
                logger.warning(f"Could not load config from {self.config_path}: {e}")
                return {}
        return {}

    def save_config(self):
        """Save configuration to file."""
        try:
            import yaml

            # Validate the config path
            PathValidator.is_safe_path(self.config_path)
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with SecureFileHandler.safe_open(self.config_path, "w") as f:
                yaml.dump(self.config, f)
        except SecurityError as e:
            logger.error(f"Security error saving config: {e}")
        except Exception as e:
            logger.warning(f"Could not save config to {self.config_path}: {e}")

    def get_model_properties(self, model_type, model_size=None):
        """Get model properties for a given type and size."""
        if model_type == "esm2":
            model_sizes = {
                "6m": "esm2_t6_8M_UR50D",
                "30m": "esm2_t12_35M_UR50D",
                "150m": "esm2_t30_150M_UR50D",
                "650m": "esm2_t33_650M_UR50D",
                "3b": "esm2_t36_3B_UR50D",
                "15b": "esm2_t48_15B_UR50D",
            }
            size = model_size or "6m"
            return {
                "model_name": model_sizes.get(size, model_sizes["6m"]),
                "model_size": size,
            }
        elif model_type == "esmc":
            model_sizes = {
                "300m": "ESMC_300M_202412",
                "600m": "ESMC_600M_202412",
            }
            size = model_size or "300m"
            return {
                "model_name": model_sizes.get(size, model_sizes["300m"]),
                "model_size": size,
            }
        elif model_type == "multimodal":
            # Example for a hypothetical multimodal model
            model_sizes = {
                "small": "your-model/small-variant",
                "medium": "your-model/medium-variant",
                "large": "your-model/large-variant",
            }
            size = model_size or "medium"
            return {
                "model_name": model_sizes.get(size, model_sizes["medium"]),
                "model_size": size,
            }
        else:
            # Default to ESM-2 for unknown model types
            logger.warning(f"Unknown model type '{model_type}', defaulting to esm2")
            return self.get_model_properties("esm2", model_size)

    def get_feature_validator(self, model_type: str):
        """Get the feature validator for a model type."""
        if model_type not in FEATURE_VALIDATORS:
            raise ValueError(
                f"Unknown model type: {model_type}. Available types: {list(FEATURE_VALIDATORS.keys())}"
            )
        return FEATURE_VALIDATORS[model_type]

    def validate_dataset_features(
        self, model_type: str, data_paths: List[str], features: Dict[str, str]
    ) -> Dict[str, str]:
        """Validate features across all dataset files."""
        validator = self.get_feature_validator(model_type)

        # Validate features for each dataset file
        for data_path in data_paths:
            # Validate the path for security
            try:
                PathValidator.is_safe_path(data_path)
            except SecurityError as e:
                raise ValueError(f"Invalid data file path: {e}")

            if not os.path.exists(data_path):
                raise ValueError(f"Data file not found: {data_path}")
            validator.validate_features(data_path, features)

        # Return the validated features (they should be consistent across all files)
        return validator.validate_features(data_paths[0], features)

    def train_model(self, args):
        """Generic training method that delegates to model-specific training."""
        model_type = args.model_type

        # Validate features
        data_paths = [args.train_data, args.val_data, args.test_data]
        features = {}

        # Extract features from args
        if hasattr(args, "sequence_column") and args.sequence_column:
            features["sequence"] = args.sequence_column
        if hasattr(args, "label_column") and args.label_column:
            features["label"] = args.label_column

        try:
            validated_features = self.validate_dataset_features(
                model_type, data_paths, features
            )
        except ValueError as e:
            logger.error(f"Feature validation failed: {e}")
            try:
                validator = self.get_feature_validator(model_type)
                logger.error(f"\n{validator.get_feature_help()}")
            except ValueError:
                logger.error(f"Unknown model type: {model_type}")
                logger.error(
                    f"Available model types: {list(FEATURE_VALIDATORS.keys())}"
                )
            return None

        # Delegate to model-specific training
        if model_type == "esm2":
            return self.train_esm2(args, validated_features)
        elif model_type == "esmc":
            return self.train_esmc(args, validated_features)
        else:
            logger.error(f"Unknown model type: {model_type}")
            logger.error(f"Available model types: {list(FEATURE_VALIDATORS.keys())}")
            return None

    def train_esm2(self, args, validated_features: Dict[str, str]):
        """Train an ESM-2 model with validated features."""
        logger.info(f"Starting ESM-2 training with model size: {args.model_size}")

        # Get model properties
        model_props = self.get_model_properties(args.model_type, args.model_size)
        args.model_name = model_props["model_name"]

        return self.train_custom(args, validated_features)

    def train_esmc(self, args, validated_features: Dict[str, str]):
        """Train an ESMC model with validated features."""
        logger.info(f"Starting ESMC training with model size: {args.model_size}")

        # Get model properties
        model_props = self.get_model_properties(args.model_type, args.model_size)
        args.model_name = model_props["model_name"]

        return self.train_custom_esmc(args, validated_features)

    def train_custom(self, args, validated_features: Dict[str, str]):
        """Train a custom model with user-specified datasets and validated features."""
        logger.info("Starting custom training...")

        # Lazy import of training modules
        from vaultide.esm2.training_pipeline import run_full_pipeline

        # Validate that all required paths are provided
        train_data = args.train_data
        val_data = args.val_data
        test_data = args.test_data

        if not all([train_data, val_data, test_data]):
            logger.error("Please provide train_data, val_data, and test_data paths")
            logger.error(
                "Use: vaultide train esm2 --train-data <path> --val-data <path> --test-data <path>"
            )
            return None

        # Validate that files exist and are secure
        for path_name, path in [
            ("train_data", train_data),
            ("val_data", val_data),
            ("test_data", test_data),
        ]:
            # Validate the path for security
            try:
                PathValidator.is_safe_path(path)
            except SecurityError as e:
                logger.error(f"Invalid {path_name} path: {e}")
                return None

            if not os.path.exists(path):
                logger.error(f"{path_name} file not found: {path}")
                return None

        # Validate custom LoRA name if provided
        lora_name = getattr(args, "name", None)
        if lora_name:
            try:
                lora_name = PathValidator.validate_model_name(lora_name)
            except SecurityError as e:
                logger.error(f"Invalid LoRA name: {e}")
                return None

        # Run the generic pipeline with validated features
        results = run_full_pipeline(
            baseline_batch_size=args.baseline_batch_size,
            lora_batch_size=args.lora_batch_size,
            num_epochs=args.epochs,
            learning_rate=args.learning_rate,
            lora_r=args.lora_r,
            lora_alpha=args.lora_alpha,
            model_size=args.model_size,
            train_baseline=not args.no_baseline,
            train_data_path=train_data,
            val_data_path=val_data,
            test_data_path=test_data,
            features=validated_features,
            lora_name=lora_name,
        )

        # Print results
        print("\n" + "=" * 60)
        print("TRAINING COMPLETED")
        print("=" * 60)

        if results["baseline_metrics"]:
            print(f"Baseline AUROC: {results['baseline_metrics']['auroc']:.4f}")
            print(f"Baseline AUPRC: {results['baseline_metrics']['auprc']:.4f}")
            print(f"Baseline MCC:   {results['baseline_metrics']['mcc']:.4f}")

        print(f"Final AUROC: {results['final_metrics']['auroc']:.4f}")
        print(f"Final AUPRC: {results['final_metrics']['auprc']:.4f}")
        print(f"Final MCC:   {results['final_metrics']['mcc']:.4f}")

        if results["baseline_metrics"]:
            auroc_improvement = (
                results["final_metrics"]["auroc"] - results["baseline_metrics"]["auroc"]
            )
            auprc_improvement = (
                results["final_metrics"]["auprc"] - results["baseline_metrics"]["auprc"]
            )
            mcc_improvement = (
                results["final_metrics"]["mcc"] - results["baseline_metrics"]["mcc"]
            )

            print(f"AUROC Improvement: {auroc_improvement:+.4f}")
            print(f"AUPRC Improvement: {auprc_improvement:+.4f}")
            print(f"MCC Improvement:   {mcc_improvement:+.4f}")

        print(f"Model saved to: {results['lora_metrics']['model_path']}")
        print("=" * 60)

        return results

    def train_custom_esmc(self, args, validated_features: Dict[str, str]):
        """Train a custom ESMC model with user-specified datasets and validated features."""
        logger.info("Starting custom ESMC training...")

        # Lazy import of training modules
        from vaultide.esmc.training_pipeline import run_full_pipeline

        # Validate that all required paths are provided
        train_data = args.train_data
        val_data = args.val_data
        test_data = args.test_data

        if not all([train_data, val_data, test_data]):
            logger.error("Please provide train_data, val_data, and test_data paths")
            logger.error(
                "Use: vaultide train esmc --train-data <path> --val-data <path> --test-data <path>"
            )
            return None

        # Validate that files exist and are secure
        for path_name, path in [
            ("train_data", train_data),
            ("val_data", val_data),
            ("test_data", test_data),
        ]:
            # Validate the path for security
            try:
                PathValidator.is_safe_path(path)
            except SecurityError as e:
                logger.error(f"Invalid {path_name} path: {e}")
                return None

            if not os.path.exists(path):
                logger.error(f"{path_name} file not found: {path}")
                return None

        # Validate custom LoRA name if provided
        lora_name = getattr(args, "name", None)
        if lora_name:
            try:
                lora_name = PathValidator.validate_model_name(lora_name)
            except SecurityError as e:
                logger.error(f"Invalid LoRA name: {e}")
                return None

        # Set default model size if not provided
        model_size = args.model_size or "6m"

        # Run the generic pipeline with validated features
        results = run_full_pipeline(
            baseline_batch_size=args.baseline_batch_size,
            lora_batch_size=args.lora_batch_size,
            num_epochs=args.epochs,
            learning_rate=args.learning_rate,
            lora_r=args.lora_r,
            lora_alpha=args.lora_alpha,
            model_size=model_size,
            train_baseline=not args.no_baseline,
            train_data_path=train_data,
            val_data_path=val_data,
            test_data_path=test_data,
            features=validated_features,
            lora_name=lora_name,
        )

        # Print results
        print("\n" + "=" * 60)
        print("ESMC TRAINING COMPLETED")
        print("=" * 60)

        if "baseline_results" in results:
            baseline_results = results["baseline_results"]
            print(f"Baseline AUROC: {baseline_results['validation']['auroc']:.4f}")
            print(f"Baseline AUPRC: {baseline_results['validation']['auprc']:.4f}")
            print(f"Baseline MCC:   {baseline_results['validation']['mcc']:.4f}")

        final_results = results["final_evaluation"]
        print(f"Final AUROC: {final_results['AUROC']:.4f}")
        print(f"Final AUPRC: {final_results['AUPRC']:.4f}")
        print(f"Final MCC:   {final_results['MCC']:.4f}")

        if "baseline_results" in results:
            baseline_results = results["baseline_results"]
            auroc_improvement = (
                final_results["AUROC"] - baseline_results["validation"]["auroc"]
            )
            auprc_improvement = (
                final_results["AUPRC"] - baseline_results["validation"]["auprc"]
            )
            mcc_improvement = (
                final_results["MCC"] - baseline_results["validation"]["mcc"]
            )

            print("\nImprovements:")
            print(f"AUROC: {auroc_improvement:+.4f}")
            print(f"AUPRC: {auprc_improvement:+.4f}")
            print(f"MCC:   {mcc_improvement:+.4f}")

        print(f"\nModel saved to: {results['lora_results']['model_path']}")
        print(f"Total training time: {results['total_time_seconds']:.2f} seconds")

        return results

    def list_models(self, args):
        """List available base models that can be used for training."""
        # Define models for each type
        model_definitions = {
            "esm2": [
                ("esm2", "6m", "esm2_t6_8M_UR50D", "6 layers, 8M params"),
                ("esm2", "30m", "esm2_t12_35M_UR50D", "12 layers, 35M params"),
                (
                    "esm2",
                    "150m",
                    "esm2_t30_150M_UR50D",
                    "30 layers, 150M params",
                ),
                (
                    "esm2",
                    "650m",
                    "esm2_t33_650M_UR50D",
                    "33 layers, 650M params",
                ),
                ("esm2", "3b", "esm2_t36_3B_UR50D", "36 layers, 3B params"),
                ("esm2", "15b", "esm2_t48_15B_UR50D", "48 layers, 15B params"),
            ],
            "esmc": [
                (
                    "esmc",
                    "300m",
                    "ESMC_300M_202412",
                    "ESMC 300M parameter model",
                ),
                (
                    "esmc",
                    "600m",
                    "ESMC_600M_202412",
                    "ESMC 600M parameter model",
                ),
            ],
        }

        # Combine all models
        models = []
        for model_type, model_list in model_definitions.items():
            models.extend(model_list)

        if getattr(args, "json", False):
            # JSON output for machine parsing
            output = {
                "models": [
                    {
                        "type": model_type,
                        "size": size,
                        "model_name": model_name,
                        "description": description,
                        "features": self.get_model_features(model_type),
                    }
                    for model_type, size, model_name, description in models
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            # Standard Unix tool output with aligned columns
            # Calculate column widths
            type_width = max(
                len("TYPE"), max(len(model_type) for model_type, _, _, _ in models)
            )
            size_width = max(len("SIZE"), max(len(size) for _, size, _, _ in models))
            model_width = max(
                len("MODEL_NAME"),
                max(len(model_name) for _, _, model_name, _ in models),
            )
            desc_width = max(
                len("DESCRIPTION"),
                max(len(description) for _, _, _, description in models),
            )

            # Print header
            header = f"{'TYPE':<{type_width}}  {'SIZE':<{size_width}}  {'MODEL_NAME':<{model_width}}  {'DESCRIPTION':<{desc_width}}"
            print(header)

            # Print data rows
            for model_type, size, model_name, description in models:
                row = f"{model_type:<{type_width}}  {size:<{size_width}}  {model_name:<{model_width}}  {description:<{desc_width}}"
                print(row)

    def get_model_features(self, model_type: str) -> Dict[str, Any]:
        """Get feature information for a model type."""
        try:
            validator = self.get_feature_validator(model_type)
            return {
                "required_features": list(validator.required_features),
                "optional_features": list(validator.optional_features),
                "feature_descriptions": validator.feature_descriptions,
            }
        except ValueError:
            return {"error": f"Unknown model type: {model_type}"}

    def show_model_features(self, model_type: str):
        """Show detailed feature information for a model type."""
        try:
            validator = self.get_feature_validator(model_type)
            print(validator.get_feature_help())
        except ValueError as e:
            logger.error(f"Error: {e}")
            logger.error(f"Available model types: {list(FEATURE_VALIDATORS.keys())}")

    def list_loras(self, args):
        """List trained LoRA models with detailed information."""
        # Determine the model-specific LoRA directory
        model_type = getattr(args, "model_type", "esm2")  # Default to esm2
        lora_base = args.lora_base or get_lora_base_path(model_type)

        # Validate the lora_base path for security
        try:
            PathValidator.is_safe_path(lora_base)
        except SecurityError as e:
            logger.error(f"Invalid LoRA base path: {e}")
            if getattr(args, "json", False):
                print(
                    json.dumps({"models": [], "error": f"Invalid LoRA base path: {e}"})
                )
            else:
                print(f"Error: Invalid LoRA base path: {e}")
            return

        if not os.path.exists(lora_base):
            if getattr(args, "json", False):
                print(
                    json.dumps(
                        {"models": [], "error": f"No LoRA models found at: {lora_base}"}
                    )
                )
            else:
                print(f"No LoRA models found at: {lora_base}")
            return

        models = []

        for item in os.listdir(lora_base):
            item_path = os.path.join(lora_base, item)
            if os.path.isdir(item_path):
                # Check if it contains LoRA files
                lora_files = [
                    f
                    for f in os.listdir(item_path)
                    if f.endswith(".bin") or f.endswith(".safetensors")
                ]
                if lora_files:
                    # Extract model info from config files
                    model_info = self.extract_model_info(item_path, item)

                    # Use directory name as the primary identifier
                    model_id = item

                    models.append((model_id, item, len(lora_files), model_info))

        if getattr(args, "json", False):
            # JSON output for machine parsing
            output = {
                "models": [
                    {
                        "model_id": model_id,
                        "directory_name": directory_name,
                        "custom_name": self._is_custom_name(directory_name),
                        "lora_files_count": file_count,
                        "base_model": model_info.get("base_model", "unknown")
                        if model_info
                        else "unknown",
                        "training_date": model_info.get("training_date", "unknown")
                        if model_info
                        else "unknown",
                        "model_info": model_info,
                    }
                    for model_id, directory_name, file_count, model_info in models
                ],
                "lora_base": lora_base,
            }
            print(json.dumps(output, indent=2))
        else:
            # Standard Unix tool output with aligned columns
            if not models:
                print(
                    "MODEL_ID                              NAME                                FILES  BASE_MODEL                    TRAINING_DATE"
                )
                return

            # Calculate column widths
            id_width = max(
                len("MODEL_ID"), max(len(model_id) for model_id, _, _, _ in models)
            )
            name_width = max(
                len("NAME"),
                max(
                    len(self._get_display_name(directory_name))
                    for _, directory_name, _, _ in models
                ),
            )
            files_width = max(
                len("FILES"),
                max(len(str(file_count)) for _, _, file_count, _ in models),
            )
            base_model_width = max(
                len("BASE_MODEL"),
                max(
                    len(
                        model_info.get("base_model", "unknown")
                        if model_info
                        else "unknown"
                    )
                    for _, _, _, model_info in models
                ),
            )
            date_width = max(
                len("TRAINING_DATE"),
                max(
                    len(
                        model_info.get("training_date", "unknown")
                        if model_info
                        else "unknown"
                    )
                    for _, _, _, model_info in models
                ),
            )

            # Print header
            header = f"{'MODEL_ID':<{id_width}}  {'NAME':<{name_width}}  {'FILES':<{files_width}}  {'BASE_MODEL':<{base_model_width}}  {'TRAINING_DATE':<{date_width}}"
            print(header)

            # Print data rows
            for model_id, directory_name, file_count, model_info in sorted(
                models, key=lambda x: x[0]
            ):
                display_name = self._get_display_name(directory_name)
                base_model = (
                    model_info.get("base_model", "unknown") if model_info else "unknown"
                )
                training_date = (
                    model_info.get("training_date", "unknown")
                    if model_info
                    else "unknown"
                )

                row = f"{model_id:<{id_width}}  {display_name:<{name_width}}  {file_count:<{files_width}}  {base_model:<{base_model_width}}  {training_date:<{date_width}}"
                print(row)

    def extract_model_info(self, model_path, model_id):
        """Extract model information from config files."""
        # Check for config files that might contain training info
        config_files = ["adapter_config.json", "config.json", "training_args.json"]

        model_info = {}

        # First, try to get base model from adapter_config.json
        adapter_config_path = os.path.join(model_path, "adapter_config.json")
        if os.path.exists(adapter_config_path):
            try:
                # Validate the model path and config file
                PathValidator.is_safe_path(model_path)
                config = SecureFileHandler.safe_read_json(adapter_config_path)

                if "base_model_name_or_path" in config:
                    model_info["base_model"] = config["base_model_name_or_path"]

                    # Extract model size from the base model name
                    if "esm2_t6_8M" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "8m"
                    elif "esm2_t12_35M" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "35m"
                    elif "esm2_t30_150M" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "150m"
                    elif "esm2_t33_650M" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "650m"
                    elif "esm2_t36_3B" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "3b"
                    elif "esm2_t48_15B" in config["base_model_name_or_path"]:
                        model_info["model_size"] = "15b"

                # Extract model_id if available
                if "model_id" in config:
                    model_info["model_id"] = config["model_id"]

            except (SecurityError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not read model config: {e}")
                pass

        # Try to get training date from directory creation time
        try:
            stat_info = os.stat(model_path)
            # Use creation time if available, otherwise modification time
            creation_time = (
                stat_info.st_ctime
                if hasattr(stat_info, "st_ctime")
                else stat_info.st_mtime
            )
            from datetime import datetime

            training_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
            model_info["training_date"] = training_date
        except (OSError, ValueError):
            model_info["training_date"] = "unknown"

        # Extract additional training parameters from config files
        for config_file in config_files:
            config_path = os.path.join(model_path, config_file)
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)

                    # Extract relevant information
                    info_parts = []

                    if "model_size" in config:
                        info_parts.append(f"size: {config['model_size']}")

                    if "task" in config:
                        info_parts.append(f"task: {config['task']}")

                    if "num_epochs" in config:
                        info_parts.append(f"epochs: {config['num_epochs']}")

                    if "learning_rate" in config:
                        info_parts.append(f"lr: {config['learning_rate']}")

                    if info_parts:
                        model_info["training_params"] = ", ".join(info_parts)

                except (json.JSONDecodeError, KeyError):
                    continue

        return model_info if model_info else None

    def _is_custom_name(self, model_id: str) -> bool:
        """Check if a model ID represents a custom name (not an auto-generated short UUID)."""

        # 8 hex chars (short UUID) is considered auto-generated
        if re.fullmatch(r"[0-9a-f]{8}", model_id):
            return False
        # Full UUID pattern (legacy)
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if re.match(uuid_pattern, model_id):
            return False
        return True

    def _get_display_name(self, model_id: str) -> str:
        """Get the display name for a model ID."""

        # Full UUID pattern - show first 8 chars as name
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if re.match(uuid_pattern, model_id):
            return model_id[:8]  # First 8 chars of UUID
        # 8 hex chars (short UUID) - show as is
        if re.fullmatch(r"[0-9a-f]{8}", model_id):
            return model_id
        # Custom name - show as is
        return model_id

    def predict_model(self, args):
        """Generic prediction method that delegates to model-specific prediction."""
        model_type = args.model_type

        # Model-specific prediction function mapping
        predict_functions = {
            "esm2": self.predict_esm2,
            "esmc": self.predict_esmc,
        }

        if model_type not in predict_functions:
            logger.error(f"Unknown model type: {model_type}")
            logger.error(f"Available model types: {list(predict_functions.keys())}")
            return None

        # Call the model-specific prediction function
        return predict_functions[model_type](args)

    def batch_predict_model(self, args):
        """Generic batch prediction method that delegates to model-specific batch prediction."""
        model_type = args.model_type

        # Model-specific batch prediction function mapping
        batch_predict_functions = {
            "esm2": self.batch_predict_esm2,
            "esmc": self.batch_predict_esmc,
        }

        if model_type not in batch_predict_functions:
            logger.error(f"Unknown model type: {model_type}")
            logger.error(
                f"Available model types: {list(batch_predict_functions.keys())}"
            )
            return None

        # Call the model-specific batch prediction function
        return batch_predict_functions[model_type](args)

    def predict_esm2(self, args):
        """Run ESM-2 prediction with LoRA."""
        logger.info(f"Starting ESM-2 prediction with LoRA: {args.lora}")
        logger.info(f"LoRA strength: {args.lora_strength}")

        # Lazy import of inference modules
        from vaultide.esm2.inference import run_inference, validate_sequence

        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esm2", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esm2")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        # Validate sequence format
        sequence = args.sequence.upper()
        if not validate_sequence(sequence):
            logger.error(
                "Invalid protein sequence. Only standard amino acids (ACDEFGHIKLMNPQRSTVWY) are allowed."
            )
            return None

        # Run prediction
        try:
            result = run_inference(
                lora_name=args.lora,
                sequence=sequence,
                lora_strength=args.lora_strength,
                verbose=args.verbose,
                full_probabilities=getattr(args, "full_probabilities", False),
            )

            # Format and output results
            self._output_prediction_results(result, args, sequence)
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def predict_esmc(self, args):
        """Run ESMC prediction with LoRA."""
        logger.info(f"Starting ESMC prediction with LoRA: {args.lora}")
        logger.info(f"LoRA strength: {args.lora_strength}")

        # Lazy import of inference modules
        from vaultide.esmc.inference import predict_sequence

        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esmc", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esmc")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        # Validate sequence format
        sequence = args.sequence.upper()
        # Basic sequence validation for ESMC
        if not sequence or not isinstance(sequence, str):
            logger.error(
                "Invalid protein sequence. Sequence must be a non-empty string."
            )
            return None

        # Run prediction
        try:
            result = predict_sequence(
                sequence=sequence,
                lora_name=args.lora,
                lora_strength=args.lora_strength,
                full_probabilities=getattr(args, "full_probabilities", False),
            )

            # Format and output results
            self._output_prediction_results(result, args, sequence)
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def batch_predict_esm2(self, args):
        """Run ESM-2 batch prediction on CSV file."""
        logger.info(f"Starting ESM-2 batch prediction with LoRA: {args.lora}")
        logger.info(f"Input CSV: {args.input_csv}")
        logger.info(f"Output directory: {args.output_dir}")

        # Lazy import of batch inference modules
        from vaultide.esm2.batch_inference import run_batch_inference

        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esm2", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esm2")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        # Validate input CSV path for security
        try:
            PathValidator.is_safe_path(args.input_csv)
        except SecurityError as e:
            logger.error(f"Invalid input CSV path: {e}")
            return None

        # Validate output directory path for security
        try:
            PathValidator.is_safe_path(args.output_dir)
        except SecurityError as e:
            logger.error(f"Invalid output directory path: {e}")
            return None

        # Run batch prediction
        try:
            result = run_batch_inference(
                lora_name=args.lora,
                input_csv_path=args.input_csv,
                output_dir=args.output_dir,
                sequence_column=getattr(args, "sequence_column", None),
                lora_strength=args.lora_strength,
                full_probabilities=getattr(args, "full_probabilities", False),
                batch_size=getattr(args, "batch_size", 32),
                verbose=args.verbose,
            )

            return result

        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            return None

    def batch_predict_esmc(self, args):
        """Run ESMC batch prediction on CSV file."""
        logger.info(f"Starting ESMC batch prediction with LoRA: {args.lora}")
        logger.info(f"Input CSV: {args.input_csv}")
        logger.info(f"Output directory: {args.output_dir}")

        # Lazy import of batch inference modules
        from vaultide.esmc.batch_inference import process_batch_predictions

        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esmc", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esmc")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        # Validate input CSV path for security
        try:
            PathValidator.is_safe_path(args.input_csv)
        except SecurityError as e:
            logger.error(f"Invalid input CSV path: {e}")
            return None

        # Validate output directory path for security
        try:
            PathValidator.is_safe_path(args.output_dir)
        except SecurityError as e:
            logger.error(f"Invalid output directory path: {e}")
            return None

        # Run batch prediction
        try:
            result = process_batch_predictions(
                input_csv=args.input_csv,
                output_dir=args.output_dir,
                lora_name=args.lora,
                sequence_column=getattr(args, "sequence_column", None),
                lora_strength=args.lora_strength,
                full_probabilities=getattr(args, "full_probabilities", False),
                batch_size=getattr(args, "batch_size", 32),
            )

            return result

        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            return None

    def _output_prediction_results(self, result: Dict[str, Any], args, sequence: str):
        """Format and output prediction results based on CLI arguments."""
        if args.json:
            self._output_json_results(result, args, sequence)
        else:
            self._output_standard_results(result, args, sequence)

        if args.output_file:
            self._save_results_to_file(result, args, sequence)

    def _output_json_results(self, result: Dict[str, Any], args, sequence: str):
        """Output results in JSON format."""
        output = {
            "lora": args.lora,
            "base_model": result.get("base_model", "unknown"),
            "lora_strength": args.lora_strength,
            "sequence": sequence,
            "prediction": result["prediction"],
            "confidence": result.get("confidence", None),
            "timestamp": result.get("timestamp", None),
        }
        output_json = json.dumps(output, indent=2)

        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(output_json)
            logger.info(f"Results saved to: {args.output_file}")
        else:
            print(output_json)

    def _output_standard_results(self, result: Dict[str, Any], args, sequence: str):
        """Output results in standard format."""
        if args.verbose:
            self._output_verbose_results(result, args, sequence)
        else:
            self._output_simple_results(result)

        if args.output_file:
            self._save_results_to_file(result, args, sequence)

    def _output_verbose_results(self, result: Dict[str, Any], args, sequence: str):
        """Output verbose results with detailed information."""
        print(f"LoRA: {args.lora} ({result.get('base_model', 'unknown')})")
        print(f"LoRA Strength: {args.lora_strength}")
        print(f"Sequence: {sequence}")

        # Handle both single values and lists
        prediction = result["prediction"]
        if isinstance(prediction, list):
            print(f"Prediction: {prediction}")
        else:
            print(f"Prediction: {prediction:.4f}")

        if result.get("confidence") is not None:
            confidence = result["confidence"]
            if isinstance(confidence, list):
                print(f"Confidence: {confidence}")
            else:
                print(f"Confidence: {confidence:.4f}")

    def _output_simple_results(self, result: Dict[str, Any]):
        """Output simple results for scripting."""
        prediction = result["prediction"]
        if isinstance(prediction, list):
            print(str(prediction))
        else:
            print(f"{prediction:.4f}")

    def _save_results_to_file(self, result: Dict[str, Any], args, sequence: str):
        """Save results to output file."""
        # Validate the output file path for security
        try:
            PathValidator.is_safe_path(args.output_file)
        except SecurityError as e:
            logger.error(f"Invalid output file path: {e}")
            return

        with SecureFileHandler.safe_open(args.output_file, "w") as f:
            if args.verbose:
                f.write(f"LoRA: {args.lora} ({result.get('base_model', 'unknown')})\n")
                f.write(f"LoRA Strength: {args.lora_strength}\n")
                f.write(f"Sequence: {sequence}\n")

                # Handle both single values and lists
                prediction = result["prediction"]
                if isinstance(prediction, list):
                    f.write(f"Prediction: {prediction}\n")
                else:
                    f.write(f"Prediction: {prediction:.4f}\n")

                if result.get("confidence") is not None:
                    confidence = result["confidence"]
                    if isinstance(confidence, list):
                        f.write(f"Confidence: {confidence}\n")
                    else:
                        f.write(f"Confidence: {confidence:.4f}\n")
            else:
                prediction = result["prediction"]
                if isinstance(prediction, list):
                    f.write(f"{prediction}\n")
                else:
                    f.write(f"{prediction:.4f}\n")

        logger.info(f"Results saved to: {args.output_file}")

    def serve_model(self, args):
        """Start FastAPI server for model predictions."""
        model_type = args.model_type
        logger.info(f"Starting prediction server for model type: {model_type}")

        # Validate model type for security
        try:
            PathValidator.validate_model_name(model_type)
        except SecurityError as e:
            logger.error(f"Invalid model type: {e}")
            return None

        # Model-specific serve function mapping
        serve_functions = {
            "esm2": self._serve_esm2,
            "esmc": self._serve_esmc,
        }

        if model_type not in serve_functions:
            logger.error(f"Unknown model type: {model_type}")
            logger.error(f"Available models: {list(serve_functions.keys())}")
            return None

        # Call the model-specific serve function
        serve_functions[model_type](args)

    def _serve_esm2(self, args):
        """Serve ESM-2 model."""
        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esm2", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esm2")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        try:
            from vaultide.esm2 import serve_esm2

            serve_esm2(
                lora_name=validated_lora_name,
                lora_strength=args.lora_strength,
                host=args.host,
                port=args.port,
                verbose=args.verbose,
            )
        except ImportError as e:
            logger.error(f"Failed to import ESM-2 serve module: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to start ESM-2 server: {e}")
            return None

    def _serve_esmc(self, args):
        """Serve ESMC model."""
        # Validate LoRA name for security
        try:
            validated_lora_name = PathValidator.validate_model_name(args.lora)
        except SecurityError as e:
            logger.error(f"Invalid LoRA name: {e}")
            return None

        # Validate LoRA exists and is secure
        lora_path = os.path.join(DEFAULT_LORA_BASE, "esmc", validated_lora_name)
        try:
            PathValidator.is_safe_path(lora_path)
        except SecurityError as e:
            logger.error(f"Invalid LoRA path: {e}")
            return None

        if not os.path.exists(lora_path):
            logger.error(f"LoRA model not found: {args.lora}")
            logger.error("Available LoRAs can be listed with: vaultide list loras esmc")
            return None

        # Validate the model directory and files
        try:
            ModelValidator.validate_model_directory(lora_path)
        except SecurityError as e:
            logger.error(f"LoRA model validation failed: {e}")
            return None

        try:
            from vaultide.esmc import serve_esmc

            serve_esmc(
                lora_name=validated_lora_name,
                lora_strength=args.lora_strength,
                host=args.host,
                port=args.port,
                verbose=args.verbose,
            )
        except ImportError as e:
            logger.error(f"Failed to import ESMC serve module: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to start ESMC server: {e}")
            return None
