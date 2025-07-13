# tests/test_train.py

import pytest
import os
from training.train import parse_args, setup_logging

def test_parse_args_defaults(tmp_path, monkeypatch):
    # Ensure default args parse correctly without environment overrides
    monkeypatch.delenv("BASE_MODEL", raising=False)
    args = parse_args()
    assert args.model_name == "granite/granite-model"
    assert args.dataset_name == "wikitext"
    assert args.dataset_config == "wikitext-2-raw-v1"
    assert args.output_dir == "./outputs"
    assert args.epochs == 3
    assert args.batch_size == 4

def test_setup_logging_caplog(caplog):
    setup_logging()
    assert "Logger initialized" in caplog.text
