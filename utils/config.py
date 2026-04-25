"""
Configuration loader for the AI-Powered Payment Fraud Detection System.

Loads settings from config.yaml with environment-variable overrides.
Follows the 12-Factor App methodology: config in the environment.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from utils.constants import (
    DEFAULT_API_HOST,
    DEFAULT_API_PORT,
    DEFAULT_DB_PATH,
    DEFAULT_MODEL_DIR,
)

# Load .env file if present (development convenience)
load_dotenv()

# Project root is two levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml_config() -> dict[str, Any]:
    """Load configuration from config.yaml at project root."""
    config_path = PROJECT_ROOT / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml_cfg = _load_yaml_config()


class Settings:
    """
    Application settings resolved in priority order:
        1. Environment variables (highest priority)
        2. config.yaml values
        3. Coded defaults (lowest priority)
    """

    # -- Server --
    API_HOST: str = os.getenv("API_HOST", _yaml_cfg.get("api_host", DEFAULT_API_HOST))
    API_PORT: int = int(os.getenv("API_PORT", _yaml_cfg.get("api_port", DEFAULT_API_PORT)))

    # -- Database --
    DB_PATH: str = os.getenv(
        "DB_PATH",
        str(PROJECT_ROOT / _yaml_cfg.get("db_path", DEFAULT_DB_PATH)),
    )

    # -- Model artifacts --
    MODEL_DIR: str = os.getenv(
        "MODEL_DIR",
        str(PROJECT_ROOT / _yaml_cfg.get("model_dir", DEFAULT_MODEL_DIR)),
    )

    # -- Logging --
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", _yaml_cfg.get("log_level", "INFO")).upper()
    LOG_FILE: str = os.getenv(
        "LOG_FILE",
        str(PROJECT_ROOT / _yaml_cfg.get("log_file", "logs/app.log")),
    )

    # -- Data generation --
    NUM_TRANSACTIONS: int = int(
        os.getenv("NUM_TRANSACTIONS", _yaml_cfg.get("num_transactions", 10_000))
    )
    FRAUD_RATIO: float = float(
        os.getenv("FRAUD_RATIO", _yaml_cfg.get("fraud_ratio", 0.03))
    )

    # -- Generative AI (LLM Explanations) --
    LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str | None = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/llama-3-8b-instruct:free")

    # -- Frontend --
    STREAMLIT_PORT: int = int(
        os.getenv("STREAMLIT_PORT", _yaml_cfg.get("streamlit_port", 8501))
    )
    BACKEND_URL: str = os.getenv(
        "BACKEND_URL",
        _yaml_cfg.get("backend_url", f"http://localhost:{API_PORT}"),
    )


settings = Settings()
