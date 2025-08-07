"""
Main entry point for Vaultide CLI.

This module contains the click-based CLI implementation for Vaultide.
"""

import logging

import click

from .cli import VaultideCLI
from vaultide.config import get_config_path, get_lora_base_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vaultide")


@click.group()
@click.option(
    "--config",
    default=get_config_path(),
    help=f"Configuration file path (default: {get_config_path()})",
)
@click.pass_context
def cli(ctx, config):
    """Vaultide - Feature-agnostic CLI for training biomolecular model LoRAs.

    Supports .bin and .safetensors formats for model storage.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


# Train command - model agnostic
@cli.command()
@click.argument("model_type", type=str, required=True)
@click.option(
    "--model-size",
    type=str,
    help="Model size variant (default varies by model type)",
)
@click.option("--train-data", required=True, help="Path to training data CSV")
@click.option("--val-data", required=True, help="Path to validation data CSV")
@click.option("--test-data", required=True, help="Path to test data CSV")
@click.option(
    "--baseline-batch-size",
    type=int,
    default=16,
    help="Baseline training batch size (default: 16)",
)
@click.option(
    "--lora-batch-size",
    type=int,
    default=8,
    help="LoRA training batch size (default: 8)",
)
@click.option(
    "--epochs", type=int, default=5, help="Number of training epochs (default: 5)"
)
@click.option(
    "--learning-rate",
    type=float,
    default=1e-4,
    help="Learning rate (default: 1e-4)",
)
@click.option("--lora-r", type=int, default=8, help="LoRA rank (default: 8)")
@click.option("--lora-alpha", type=int, default=16, help="LoRA alpha (default: 16)")
@click.option("--no-baseline", is_flag=True, help="Skip baseline model training")
@click.option(
    "--sequence-column",
    help="Name of sequence column in CSV (auto-detected if not specified)",
)
@click.option(
    "--label-column",
    default="label",
    help="Name of label column in CSV (default: label)",
)
@click.option(
    "--name",
    help="Custom name for the LoRA model (optional, auto-generated if not provided)",
)
@click.pass_context
def train(ctx, model_type, **kwargs):
    """Train a biomolecular model with LoRA fine-tuning.

    MODEL_TYPE: Type of model to train (e.g., esm2, multimodal)
    """
    cli_instance = VaultideCLI(ctx.obj["config"])

    # Create a mock args object with the kwargs
    class Args:
        def __init__(self, model_type, **kwargs):
            self.model_type = model_type
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(model_type, **kwargs)
    cli_instance.train_model(args)


# List command group
@cli.group()
def list():
    """List available models or trained LoRAs."""
    pass


@list.command()
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_context
def models(ctx, json):
    """List available base models for training."""
    cli_instance = VaultideCLI(ctx.obj["config"])

    class Args:
        def __init__(self, json=False):
            self.json = json

    args = Args(json=json)
    cli_instance.list_models(args)


@list.command()
@click.argument("model_type", default="esm2")
@click.option(
    "--lora-base",
    help=f"Base directory for LoRA models (default: {get_lora_base_path('esm2')})",
)
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_context
def loras(ctx, model_type, lora_base, json):
    """List trained LoRA models.

    MODEL_TYPE: Type of model to list LoRAs for (default: esm2)
    """
    cli_instance = VaultideCLI(ctx.obj["config"])

    class Args:
        def __init__(self, model_type, lora_base, json=False):
            self.model_type = model_type
            self.lora_base = lora_base
            self.json = json

    args = Args(model_type, lora_base, json)
    cli_instance.list_loras(args)


# Features command
@cli.command()
@click.argument("model_type")
def features(model_type):
    """Show feature information for model types.

    MODEL_TYPE: Type of model to show features for
    """
    cli_instance = VaultideCLI()
    cli_instance.show_model_features(model_type)


# Predict command - model agnostic
@cli.command()
@click.argument("model_type", type=str, required=True)
@click.option("--lora", required=True, help="Name of the LoRA model to use")
@click.option("--sequence", required=True, help="Protein sequence to predict on")
@click.option(
    "--lora-strength",
    type=float,
    default=1.0,
    help="LoRA strength (0.0 = base model only, 1.0 = full LoRA, >1.0 = amplified) (default: 1.0)",
)
@click.option(
    "--full-probabilities",
    is_flag=True,
    help="Return full probability distribution instead of just positive class probability",
)
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.option("--output-file", help="Save results to file")
@click.pass_context
def predict(ctx, model_type, **kwargs):
    """Run prediction with trained LoRA.

    MODEL_TYPE: Type of model to use for prediction (e.g., esm2, multimodal)
    """
    cli_instance = VaultideCLI(ctx.obj["config"])

    class Args:
        def __init__(self, model_type, **kwargs):
            self.model_type = model_type
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(model_type, **kwargs)
    cli_instance.predict_model(args)


# Batch predict command - model agnostic
@cli.command()
@click.argument("model_type", type=str, required=True)
@click.option("--lora", required=True, help="Name of the LoRA model to use")
@click.option(
    "--input-csv", required=True, help="Path to input CSV file containing sequences"
)
@click.option(
    "--output-dir",
    required=True,
    help="Directory to save output CSV and metadata files",
)
@click.option(
    "--sequence-column",
    help="Name of sequence column in CSV (auto-detected if not specified)",
)
@click.option(
    "--lora-strength",
    type=float,
    default=1.0,
    help="LoRA strength (0.0 to 2.0, default: 1.0)",
)
@click.option(
    "--full-probabilities",
    is_flag=True,
    help="Return full probability distribution instead of just positive class probability",
)
@click.option(
    "--batch-size",
    type=int,
    default=32,
    help="Batch size for processing (default: 32)",
)
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.pass_context
def batch_predict(ctx, model_type, **kwargs):
    """Run batch predictions on CSV files.

    MODEL_TYPE: Type of model to use for batch prediction (e.g., esm2, multimodal)
    """
    cli_instance = VaultideCLI(ctx.obj["config"])

    class Args:
        def __init__(self, model_type, **kwargs):
            self.model_type = model_type
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(model_type, **kwargs)
    cli_instance.batch_predict_model(args)


# Serve command - model agnostic
@cli.command()
@click.argument("model_type", type=str, required=True)
@click.option("--lora", required=True, help="Name of the LoRA model to use")
@click.option(
    "--lora-strength",
    type=float,
    default=1.0,
    help="LoRA strength (0.0 = base model only, 1.0 = full LoRA, >1.0 = amplified) (default: 1.0)",
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind server to (default: 127.0.0.1)",
)
@click.option(
    "--port", type=int, default=8000, help="Port to bind server to (default: 8000)"
)
@click.option("--verbose", is_flag=True, help="Show verbose server logs")
@click.pass_context
def serve(ctx, model_type, **kwargs):
    """Start FastAPI server for predictions.

    MODEL_TYPE: Type of model to serve (e.g., esm2, multimodal)
    """
    cli_instance = VaultideCLI(ctx.obj["config"])

    class Args:
        def __init__(self, model_type, **kwargs):
            self.model_type = model_type
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(model_type, **kwargs)
    cli_instance.serve_model(args)


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
