import argparse
import logging
import pandas as pd
from vaultide.esm2.training_pipeline import train_lora

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_best_lora_rank(
    ranks,
    train_data_path,
    val_data_path,
    sequence_column,
    label_column,
    model_size,
    epochs,
    learning_rate,
    lora_alpha=None
):
    """
    Performs a grid search over a list of LoRA ranks to find the best one based on validation AUPRC.

    Args:
        ranks (list): A list of integer ranks to test.
        train_data_path (str): Path to the training data CSV.
        val_data_path (str): Path to the validation data CSV.
        sequence_column (str): The name of the sequence column in the CSV files.
        label_column (str): The name of the label column in the CSV files.
        model_size (str): The ESM-2 model size to use (e.g., "8m", "650m").
        epochs (int): The number of epochs to train for each rank.
        learning_rate (float): The learning rate for the optimizer.
        lora_alpha (int, optional): A fixed LoRA alpha. If None, alpha will be set to 2 * rank. Defaults to None.
    """
    best_rank = None
    best_auprc = 0.0
    results = []

    logger.info("Starting LoRA rank search...")
    logger.info(f"Ranks to test: {ranks}")

    for rank in ranks:
        logger.info(f"--- Testing Rank: {rank} ---")
        
        current_lora_alpha = lora_alpha if lora_alpha is not None else 2 * rank
        logger.info(f"Using LoRA alpha: {current_lora_alpha}")

        try:
            lora_metrics = train_lora(
                train_data_path=train_data_path,
                val_data_path=val_data_path,
                sequence_column=sequence_column,
                label_column=label_column,
                model_size=model_size,
                num_epochs=epochs,
                learning_rate=learning_rate,
                lora_r=rank,
                lora_alpha=current_lora_alpha,
                lora_name=f"lora_rank_{rank}_model"
            )

            current_auprc = lora_metrics.get("best_val_auprc", 0.0)
            results.append({"rank": rank, "best_val_auprc": current_auprc})
            
            logger.info(f"Rank {rank} finished. Best Validation AUPRC: {current_auprc:.4f}")

            if current_auprc > best_auprc:
                best_auprc = current_auprc
                best_rank = rank
                logger.info(f"New best rank found: {best_rank} with AUPRC: {best_auprc:.4f}")

        except Exception as e:
            logger.error(f"An error occurred while training with rank {rank}: {e}", exc_info=True)
            results.append({"rank": rank, "best_val_auprc": "Error"})


    logger.info("\n--- Rank Search Complete ---")
    if results:
        results_df = pd.DataFrame(results)
        logger.info("Results summary:\n" + results_df.to_string(index=False))

    if best_rank is not None:
        logger.info(f"\nBest LoRA Rank: {best_rank} (AUPRC: {best_auprc:.4f})")
    else:
        logger.warning("Could not determine the best rank. Please check the logs for errors.")

    return best_rank, best_auprc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the best LoRA rank for ESM-2 model training.")
    
    # Required arguments
    parser.add_argument("--ranks", type=int, nargs='+', required=True, help="A list of LoRA ranks to test (e.g., 4 8 16).")
    parser.add_argument("--train-data", required=True, help="Path to the training data CSV file.")
    parser.add_argument("--val-data", required=True, help="Path to the validation data CSV file.")
    parser.add_argument("--model-size", required=True, help="ESM-2 model size (e.g., '8m', '35m', '650m').")

    # Optional arguments with defaults
    parser.add_argument("--sequence-column", default="sequence", help="Name of the sequence column.")
    parser.add_argument("--label-column", default="label", help="Name of the label column.")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs for each rank.")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate for the optimizer.")
    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=None,
        help="Fixed LoRA alpha parameter. If not provided, it will be set to 2 * rank for each test.",
    )

    args = parser.parse_args()

    find_best_lora_rank(
        ranks=args.ranks,
        train_data_path=args.train_data,
        val_data_path=args.val_data,
        sequence_column=args.sequence_column,
        label_column=args.label_column,
        model_size=args.model_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        lora_alpha=args.lora_alpha
    ) 
