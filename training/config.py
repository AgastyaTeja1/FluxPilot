# training/config.py

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings, Field


class ModelSettings(BaseSettings):
    base_model: str = Field(..., env="BASE_MODEL")
    max_new_tokens: int = Field(50, env="MAX_NEW_TOKENS")


class TrainingSettings(BaseSettings):
    epochs: int = Field(3, env="EPOCHS")
    batch_size: int = Field(4, env="BATCH_SIZE")


class MLflowSettings(BaseSettings):
    tracking_uri: str = Field(..., env="MLFLOW_TRACKING_URI")
    experiment_name: str = Field(..., env="MLFLOW_EXPERIMENT")


class AWSSettings(BaseSettings):
    region: str = Field(..., env="AWS_REGION")
    account_id: str = Field(..., env="AWS_ACCOUNT_ID")
    ecr_repository: str = Field(..., env="ECR_REPOSITORY")
    sagemaker_endpoint: str = Field(..., env="SAGEMAKER_ENDPOINT_NAME")
    execution_role_arn: str = Field(..., env="SAGEMAKER_EXECUTION_ROLE_ARN")
    secrets_manager_path: str = Field("/fluxpilot", env="AWS_SECRETS_PATH")


class Config:
    """
    Central configuration loader.
    Reads 'config/config.yaml', merges 'default' with the active profile,
    and instantiates settings classes with any env var overrides.
    """

    def __init__(self, profile: str = None, config_file: str = None):
        # Determine config file path
        self.config_file = (
            config_file
            or os.getenv("CONFIG_FILE", "config/config.yaml")
        )
        # Determine active profile
        self.profile = profile or os.getenv("ENV_PROFILE", "default")

        # Load and merge YAML
        raw = self._load_yaml()
        merged = self._merge_profile(raw, self.profile)

        # Instantiate settings
        self.model = ModelSettings(**merged.get("model", {}))
        self.training = TrainingSettings(**merged.get("training", {}))
        self.mlflow = MLflowSettings(**merged.get("mlflow", {}))
        self.aws = AWSSettings(**merged.get("aws", {}))

    def _load_yaml(self) -> Dict[str, Any]:
        path = Path(self.config_file)
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _merge_profile(self, raw: Dict[str, Any], profile: str) -> Dict[str, Any]:
        default_cfg = raw.get("default", {})
        profile_cfg = raw.get(profile, {})
        merged: Dict[str, Any] = {}
        # Merge each top-level section
        for section in set(default_cfg) | set(profile_cfg):
            base = default_cfg.get(section, {})
            override = profile_cfg.get(section, {})
            # Only merge dicts; otherwise override entirely
            if isinstance(base, dict) and isinstance(override, dict):
                merged[section] = {**base, **override}
            else:
                merged[section] = override or base
        return merged
