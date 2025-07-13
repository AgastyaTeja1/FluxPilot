# orchestrator/config.py

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings, Field


class PrefectSettings(BaseSettings):
    api_url: str = Field(..., env="PREFECT_API_URL")
    api_token: str = Field(..., env="PREFECT_API_TOKEN")
    flow_name: str = Field(..., env="PREFECT_FLOW_NAME")


class MLflowSettings(BaseSettings):
    tracking_uri: str = Field(..., env="MLFLOW_TRACKING_URI")
    experiment_name: str = Field(..., env="MLFLOW_EXPERIMENT")


class Config:
    """
    Load config/config.yaml, merge default + profile, and provide Prefect & MLflow settings.
    """

    def __init__(self, profile: str = None, config_file: str = None):
        # Determine config file path
        self.config_file = config_file or os.getenv("CONFIG_FILE", "config/config.yaml")
        self.profile = profile or os.getenv("ENV_PROFILE", "default")

        raw = self._load_yaml()
        merged = self._merge_profile(raw, self.profile)

        # Instantiate settings
        self.prefect = PrefectSettings(**merged.get("orchestrator", {}).get("prefect", {}))
        self.mlflow = MLflowSettings(**merged.get("mlflow", {}))

    def _load_yaml(self) -> Dict[str, Any]:
        path = Path(self.config_file)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _merge_profile(self, raw: Dict[str, Any], profile: str) -> Dict[str, Any]:
        default_cfg = raw.get("default", {})
        profile_cfg = raw.get(profile, {})
        merged: Dict[str, Any] = {}
        # Merge top-level sections
        for section in set(default_cfg) | set(profile_cfg):
            base = default_cfg.get(section, {})
            override = profile_cfg.get(section, {})
            if isinstance(base, dict) and isinstance(override, dict):
                merged[section] = {**base, **override}
            else:
                merged[section] = override or base
        return merged
