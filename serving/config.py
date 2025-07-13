# serving/config.py

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings, Field


class ServingSettings(BaseSettings):
    model_dir: str = Field(..., env="SERVE_MODEL_DIR")
    host: str = Field("0.0.0.0", env="SERVE_HOST")
    port: int = Field(8080, env="SERVE_PORT")
    workers: int = Field(4, env="GUNICORN_WORKERS")
    api_key_header: str = Field("X-API-KEY", env="API_KEY_HEADER")
    secrets_manager_key: str = Field("/fluxpilot/api_keys", env="AUTH_SECRETS_MANAGER_KEY")


class Config:
    """
    Load config/config.yaml, merge default + profile, and provide ServingSettings.
    """

    def __init__(self, profile: str = None, config_file: str = None):
        # Determine config file path
        self.config_file = config_file or os.getenv("CONFIG_FILE", "config/config.yaml")
        self.profile = profile or os.getenv("ENV_PROFILE", "default")

        raw = self._load_yaml()
        merged = self._merge_profile(raw, self.profile)
        self.serving_cfg = ServingSettings(**merged.get("serving", {}))

    def _load_yaml(self) -> Dict[str, Any]:
        path = Path(self.config_file)
        if not path.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _merge_profile(self, raw: Dict[str, Any], profile: str) -> Dict[str, Any]:
        default_cfg = raw.get("default", {})
        profile_cfg = raw.get(profile, {})
        merged: Dict[str, Any] = {}
        for section in set(default_cfg) | set(profile_cfg):
            base = default_cfg.get(section, {})
            override = profile_cfg.get(section, {})
            if isinstance(base, dict) and isinstance(override, dict):
                merged[section] = {**base, **override}
            else:
                merged[section] = override or base
        return merged
