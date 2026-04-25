"""
Model inference module for the Fraud Detection System.

Provides a singleton ModelManager that loads trained models once
and serves predictions with minimal latency.

Architecture:
    - Models are loaded into memory on first call (lazy initialization).
    - The Isolation Forest anomaly score is combined with the Logistic
      Regression probability and optional XGBoost for a robust fraud score.
    - Ensemble weights are loaded from config/fraud_thresholds.yaml.
    - Risk levels are derived from configurable thresholds.
"""

import json
import yaml
from pathlib import Path
from threading import Lock

import numpy as np
import pandas as pd
import joblib

from models.feature_engineering import engineer_features, extract_model_features
from data.preprocessor import TransactionPreprocessor
from utils.constants import (
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    FEATURE_NAMES,
    DEFAULT_ENSEMBLE_WEIGHTS,
    FALLBACK_ENSEMBLE_WEIGHTS,
)
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "fraud_thresholds.yaml"


def _load_thresholds_config() -> dict:
    """Load threshold configuration from YAML file."""
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


class ModelManager:
    """
    Singleton manager for ML model loading and inference.

    Thread-safe lazy loading ensures models are loaded exactly once,
    even under concurrent API requests.

    Supports up to 3 ensemble models:
        - Isolation Forest (anomaly detection)
        - Logistic Regression (supervised classification)
        - XGBoost (gradient boosting, optional)
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.iso_model = None
        self.lr_model = None
        self.xgb_model = None
        self.preprocessor = None
        self.lr_coefficients = None
        self.training_metrics = None
        self._models_loaded = False

        # Load configurable thresholds
        config = _load_thresholds_config()
        thresholds = config.get("risk_thresholds", {})
        self._threshold_low = thresholds.get("low_max", 0.30)
        self._threshold_high = thresholds.get("high_min", 0.70)

        # Load ensemble weights
        self._ensemble_weights = config.get("ensemble_weights", DEFAULT_ENSEMBLE_WEIGHTS)

    def load_models(self, model_dir: str | None = None) -> None:
        """
        Load all trained model artifacts from disk.

        Args:
            model_dir: Path to the artifacts directory.
                       Defaults to settings.MODEL_DIR.
        """
        artifact_dir = Path(model_dir or settings.MODEL_DIR)

        if not artifact_dir.exists():
            raise FileNotFoundError(
                f"Model artifacts not found at {artifact_dir}. "
                f"Run 'python run.py --mode train' first."
            )

        logger.info(f"Loading model artifacts from {artifact_dir}")

        # Load Isolation Forest
        iso_path = artifact_dir / "isolation_forest.joblib"
        if iso_path.exists():
            self.iso_model = joblib.load(iso_path)
            logger.info("Isolation Forest model loaded")
        else:
            logger.warning(f"Isolation Forest model not found at {iso_path}")

        # Load Logistic Regression
        lr_path = artifact_dir / "logistic_regression.joblib"
        if lr_path.exists():
            self.lr_model = joblib.load(lr_path)
            logger.info("Logistic Regression model loaded")
        else:
            logger.warning(f"Logistic Regression model not found at {lr_path}")

        # Load XGBoost (optional)
        xgb_path = artifact_dir / "xgboost.joblib"
        if xgb_path.exists():
            self.xgb_model = joblib.load(xgb_path)
            logger.info("XGBoost model loaded")
        else:
            logger.info("XGBoost model not available — using 2-model ensemble")

        # Load preprocessor (scaler)
        self.preprocessor = TransactionPreprocessor()
        try:
            self.preprocessor.load(str(artifact_dir))
        except FileNotFoundError:
            logger.warning("Scaler not found — inference will use unscaled features")

        # Load LR coefficients for explainability
        coef_path = artifact_dir / "lr_coefficients.json"
        if coef_path.exists():
            with open(coef_path, "r") as f:
                self.lr_coefficients = json.load(f)

        # Load training metrics
        metrics_path = artifact_dir / "training_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                self.training_metrics = json.load(f)

        self._models_loaded = True
        logger.info("All models loaded successfully")

    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded and ready for inference."""
        return self._models_loaded

    def predict(self, transaction_data: dict) -> dict:
        """
        Run fraud prediction on a single transaction.

        Uses adaptive ensemble weighting: if XGBoost is available,
        uses 3-model weights; otherwise falls back to 2-model weights.

        Args:
            transaction_data: Dict with raw transaction features.

        Returns:
            Dict with fraud_probability, risk_level, model_scores, and features.
        """
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # ── Feature engineering (22 features) ─────────────────────────
        df = engineer_features(transaction_data)
        X_raw = extract_model_features(df)

        # ── Scale features ────────────────────────────────────────────
        try:
            X_scaled = self.preprocessor.scaler.transform(X_raw)
        except Exception:
            logger.warning("Scaler transform failed, using raw features")
            X_scaled = X_raw

        model_scores = {}
        available_models = {}

        # ── Isolation Forest score ────────────────────────────────────
        if self.iso_model is not None:
            raw_score = self.iso_model.score_samples(X_scaled)[0]
            # Normalize: more negative = more anomalous → higher fraud score
            iso_fraud_score = max(0.0, min(1.0, -raw_score - 0.3))
            # Sigmoid calibration to 0-1 range
            iso_fraud_score = 1 / (1 + np.exp(-5 * (iso_fraud_score - 0.4)))
            model_scores["isolation_forest_score"] = float(round(iso_fraud_score, 4))
            available_models["isolation_forest"] = iso_fraud_score

        # ── Logistic Regression score ─────────────────────────────────
        if self.lr_model is not None:
            lr_proba = self.lr_model.predict_proba(X_scaled)[0][1]
            model_scores["logistic_regression_score"] = float(round(lr_proba, 4))
            available_models["logistic_regression"] = lr_proba

        # ── XGBoost score (optional) ──────────────────────────────────
        if self.xgb_model is not None:
            xgb_proba = self.xgb_model.predict_proba(X_scaled)[0][1]
            model_scores["xgboost_score"] = float(round(xgb_proba, 4))
            available_models["xgboost"] = xgb_proba

        if not available_models:
            raise RuntimeError("No models available for prediction")

        # ── Adaptive ensemble scoring ─────────────────────────────────
        fraud_probability = self._blend_scores(available_models)
        fraud_probability = float(round(fraud_probability, 4))

        # ── Risk level classification ─────────────────────────────────
        risk_level = self._classify_risk(fraud_probability)

        # ── Feature values used ───────────────────────────────────────
        feature_values = {
            name: float(X_raw[0][i]) for i, name in enumerate(FEATURE_NAMES)
        }

        return {
            "fraud_probability": fraud_probability,
            "risk_level": risk_level,
            "model_scores": model_scores,
            "feature_values": feature_values,
        }

    def _blend_scores(self, available_models: dict[str, float]) -> float:
        """
        Compute weighted ensemble score with adaptive re-normalization.

        If a model is missing, its weight is redistributed proportionally
        to the remaining models.
        """
        weights = dict(self._ensemble_weights)

        # Filter to available models only
        active_weights = {k: weights.get(k, 0) for k in available_models}
        total_weight = sum(active_weights.values())

        if total_weight == 0:
            # Equal weighting fallback
            return sum(available_models.values()) / len(available_models)

        # Re-normalize weights to sum to 1.0
        normalized = {k: v / total_weight for k, v in active_weights.items()}

        score = sum(
            normalized[model] * available_models[model]
            for model in available_models
        )

        return max(0.0, min(1.0, score))

    def _classify_risk(self, probability: float) -> str:
        """Map fraud probability to a risk level using configurable thresholds."""
        if probability < self._threshold_low:
            return RISK_LEVEL_LOW
        elif probability < self._threshold_high:
            return RISK_LEVEL_MEDIUM
        else:
            return RISK_LEVEL_HIGH


# Module-level singleton for easy import
model_manager = ModelManager()
