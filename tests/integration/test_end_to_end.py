# tests/integration/test_end_to_end.py

import os
import subprocess
import time
import requests
import pytest

MLFLOW_PORT = 5000
SERVE_PORT = 8080

@pytest.fixture(scope="session", autouse=True)
def start_services(tmp_path_factory):
    """
    Start MLflow, training (smoke), and serving via Docker Compose, then tear down.
    """
    # Launch docker-compose in detached mode
    cwd = os.getcwd()
    proc = subprocess.Popen(
        ["docker-compose", "up", "--build", "-d"],
        cwd=os.path.join(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Give services time to start
    time.sleep(60)

    yield

    # Teardown
    subprocess.run(
        ["docker-compose", "down", "-v"],
        cwd=os.path.join(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(10)

def test_generate_endpoint():
    """
    Hit the /generate endpoint and verify a JSON response with 'generated_text'.
    """
    url = f"http://localhost:{SERVE_PORT}/generate"
    payload = {"prompt": "Hello world", "max_new_tokens": 5}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)

    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
    data = resp.json()
    assert "generated_text" in data, "Response JSON must contain 'generated_text'"
    assert isinstance(data["generated_text"], str)
