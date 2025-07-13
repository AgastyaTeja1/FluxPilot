# training/data_loader.py

import logging
from datasets import load_dataset
from typing import Optional

def load_data(
    dataset_name: str,
    dataset_config: Optional[str] = None,
    split: str = "train"
):
    """
    Load a Hugging Face dataset.

    Args:
        dataset_name: Name of the dataset (e.g., "wikitext").
        dataset_config: Specific dataset configuration (e.g., "wikitext-2-raw-v1").
        split: Which split to load ("train", "validation", or "test").

    Returns:
        A Hugging Face Dataset object.
    """
    try:
        if dataset_config:
            dataset = load_dataset(dataset_name, dataset_config, split=split)
            logging.info(f"Loaded dataset {dataset_name}/{dataset_config} split={split} with {len(dataset)} examples")
        else:
            dataset = load_dataset(dataset_name, split=split)
            logging.info(f"Loaded dataset {dataset_name} split={split} with {len(dataset)} examples")
        return dataset
    except Exception as e:
        logging.error(f"Error loading dataset {dataset_name}: {e}")
        raise
