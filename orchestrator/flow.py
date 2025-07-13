# orchestrator/flow.py

import logging
import subprocess
from prefect import flow, task, get_run_logger

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger("orchestrator")


@task(retries=3, retry_delay_seconds=120)
def train_task():
    """
    Task: Invoke the training script.
    Retries up to 3 times on failure, waiting 2 minutes between attempts.
    """
    task_logger = get_run_logger()
    task_logger.info("Starting Granite LLM training…")
    # Launch the training module
    result = subprocess.run(
        ["python", "-m", "training.train"],
        check=False,
        capture_output=True,
        text=True
    )
    task_logger.info(result.stdout)
    if result.returncode != 0:
        task_logger.error(result.stderr)
        raise RuntimeError("training/train.py failed")
    task_logger.info("Training completed successfully.")


@flow(name="FluxPilot_Granite_Pipeline")
def fluxpilot_flow():
    """
    Prefect flow: orchestrates the entire pipeline.
    """
    train_task()


if __name__ == "__main__":
    fluxpilot_flow()
