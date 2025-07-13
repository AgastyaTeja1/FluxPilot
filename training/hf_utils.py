# training/hf_utils.py

import logging
from transformers import PreTrainedTokenizer
from typing import Dict, Any

def preprocess_function(
    examples: Dict[str, Any],
    tokenizer: PreTrainedTokenizer,
    max_length: int = 512,
    stride: int = 128
) -> Dict[str, Any]:
    """
    Tokenize and chunk long text sequences into overlapping windows.

    Args:
        examples: A batch of examples with a "text" field.
        tokenizer: HuggingFace tokenizer to use.
        max_length: Maximum token window size.
        stride: Number of overlapped tokens between windows.

    Returns:
        A dict of tokenized inputs suitable for Trainer.
    """
    texts = examples.get("text", [])
    # Tokenize with sliding window
    tokenized_inputs = tokenizer(
        texts,
        return_attention_mask=True,
        return_token_type_ids=False,
        truncation=True,
        max_length=max_length,
        stride=stride,
        return_overflowing_tokens=True,
        return_special_tokens_mask=True
    )

    # For overflowing tokens, label them the same as input_ids
    input_ids = tokenized_inputs["input_ids"]
    attention_masks = tokenized_inputs["attention_mask"]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_masks,
    }
