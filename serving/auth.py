# serving/auth.py

import os
import json
from typing import Set

import boto3
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from botocore.exceptions import BotoCoreError, ClientError

from serving.config import Config

# Load serving configuration
cfg = Config()

API_KEY_HEADER = cfg.serving_cfg.api_key_header  # e.g. "X-API-KEY"
SECRETS_MANAGER_KEY = cfg.serving_cfg.secrets_manager_key  # e.g. "/fluxpilot/api_keys"

api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def _load_keys_from_env() -> Set[str]:
    """
    Fallback: load API keys from an environment variable 'API_KEYS', comma-separated.
    """
    raw = os.getenv("API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def _load_keys_from_secrets_manager() -> Set[str]:
    """
    Primary: load API keys JSON from AWS Secrets Manager.
    Expect a JSON like: {"api_keys": ["key1", "key2", ...]}
    """
    try:
        client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION"))
        resp = client.get_secret_value(SecretId=SECRETS_MANAGER_KEY)
        secret_str = resp.get("SecretString", "{}")
        secret_json = json.loads(secret_str)
        return set(secret_json.get("api_keys", []))
    except (ClientError, BotoCoreError, json.JSONDecodeError):
        # If anything fails, fall back to env
        return set()


def get_allowed_api_keys() -> Set[str]:
    """
    Returns the set of allowed API keys, preferring Secrets Manager.
    """
    keys = _load_keys_from_secrets_manager()
    if keys:
        return keys
    return _load_keys_from_env()


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    FastAPI dependency to enforce API key auth.
    Raises 401 if header missing or invalid.
    """
    allowed = get_allowed_api_keys()
    if not api_key or api_key not in allowed:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
