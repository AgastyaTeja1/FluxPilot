# tests/test_serving.py

import pytest
from fastapi.testclient import TestClient
import os
import shutil

from serving.app import app

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "FluxPilot Granite API is up"}

@pytest.fixture(autouse=True)
def temp_model_dir(tmp_path, monkeypatch):
    # Create a dummy model directory with tokenizer & model files
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    # Create dummy files so AutoTokenizer/model import doesn't crash
    (model_dir / "config.json").write_text("{}")
    (model_dir / "tokenizer.json").write_text("{}")
    (model_dir / "pytorch_model.bin").write_bytes(b"")
    monkeypatch.setenv("SERVE_MODEL_DIR", str(model_dir))
    yield
    shutil.rmtree(str(model_dir))
