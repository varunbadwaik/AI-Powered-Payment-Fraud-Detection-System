"""
Model training pipeline for the Fraud Detection System.

Trains two complementary models:
    1. Isolation Forest — unsupervised anomaly detection (primary)
       Good at detecting novel fraud patterns not seen in training.
    2. Logistic Regression — supervised classification (secondary)
       Provides interpretable probability scores and feature coefficients.

Both models are saved as joblib artifacts for low-latency inference.
"""

import sys
import json
from pathlib import Path

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
)

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generator import prepare_dataset
from data.preprocessor import TransactionPreprocessor
from utils.constants import (
    ISOLATION_FOREST_PARAMS,
    LOGISTIC_REGRESSION_PARAMS,
    XGBOOST_PARAMS,
    FEATURE_NAMES,
    DEFAULT_FRAUD_RATIO,
)
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def train_isolation_forest(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> tuple[IsolationForest, dict]:
    """
    Train an Isolation Forest model for anomaly-based fraud detection.

    Isolation Forest works by randomly partitioning the feature space.
    Anomalies (fraud) require fewer partitions to isolate, yielding
    shorter average path lengths.

    Args:
        X_train: Scaled training features.
        X_test: Scaled test features.
        y_test: True labels for evaluation.

    Returns:
        Tuple of (trained model, metrics dict).
    """
    logger.info("Training Isolation Forest model...")

    model = IsolationForest(**ISOLATION_FOREST_PARAMS)
    model.fit(X_train)

    # Isolation Forest returns -1 (anomaly) or 1 (normal)
    raw_preds = model.predict(X_test)
    y_pred = np.where(raw_preds == -1, 1, 0)  # Map to 0/1 fraud labels

    # Anomaly scores (more negative = more anomalous)
    scores = model.score_samples(X_test)
    # Convert to probability-like score (0=normal, 1=fraud)
    fraud_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min())

    metrics = _evaluate_model("IsolationForest", y_test, y_pred, fraud_scores)

    return model, metrics


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> tuple[LogisticRegression, dict]:
    """
    Train a Logistic Regression model for supervised fraud classification.

    Uses balanced class weights to handle the severe class imbalance
    inherent in fraud detection (typically <5% fraud rate).

    Args:
        X_train: Scaled training features.
        y_train: Training labels.
        X_test: Scaled test features.
        y_test: True test labels.

    Returns:
        Tuple of (trained model, metrics dict).
    """
    logger.info("Training Logistic Regression model...")

    model = LogisticRegression(**LOGISTIC_REGRESSION_PARAMS)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    fraud_proba = model.predict_proba(X_test)[:, 1]

    metrics = _evaluate_model("LogisticRegression", y_test, y_pred, fraud_proba)

    return model, metrics


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> tuple[any, dict]:
    """
    Train an XGBoost model for high-accuracy supervised classification.
    """
    if not XGB_AVAILABLE:
        return None, {}

    logger.info("Training XGBoost model...")

    model = XGBClassifier(**XGBOOST_PARAMS)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    fraud_proba = model.predict_proba(X_test)[:, 1]

    metrics = _evaluate_model("XGBoost", y_test, y_pred, fraud_proba)

    return model, metrics


def _evaluate_model(
    name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    fraud_scores: np.ndarray,
) -> dict:
    """Compute and log comprehensive evaluation metrics."""
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    try:
        roc_auc = roc_auc_score(y_true, fraud_scores)
    except ValueError:
        roc_auc = 0.0

    try:
        avg_precision = average_precision_score(y_true, fraud_scores)
    except ValueError:
        avg_precision = 0.0

    metrics = {
        "model": name,
        "accuracy": report.get("accuracy", 0.0),
        "precision_fraud": report.get("1", {}).get("precision", 0.0),
        "recall_fraud": report.get("1", {}).get("recall", 0.0),
        "f1_fraud": report.get("1", {}).get("f1-score", 0.0),
        "roc_auc": roc_auc,
        "avg_precision": avg_precision,
        "confusion_matrix": cm.tolist(),
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"Model: {name}")
    logger.info(f"{'='*60}")
    logger.info(f"ROC-AUC: {roc_auc:.4f}")
    logger.info(f"Avg Precision: {avg_precision:.4f}")
    logger.info(f"Precision (fraud): {metrics['precision_fraud']:.4f}")
    logger.info(f"Recall (fraud): {metrics['recall_fraud']:.4f}")
    logger.info(f"F1 (fraud): {metrics['f1_fraud']:.4f}")
    logger.info(f"Confusion Matrix:\n{cm}")
    logger.info(f"{'='*60}\n")

    return metrics


def run_training_pipeline(
    num_transactions: int | None = None,
    fraud_ratio: float | None = None,
) -> dict:
    """
    Execute the full training pipeline:
        1. Generate synthetic data
        2. Preprocess and split
        3. Train both models
        4. Evaluate and save artifacts

    Args:
        num_transactions: Number of transactions to generate.
        fraud_ratio: Fraud ratio in generated data.

    Returns:
        Dict with paths to saved artifacts and evaluation metrics.
    """
    n_txn = num_transactions or settings.NUM_TRANSACTIONS
    f_ratio = fraud_ratio or settings.FRAUD_RATIO

    logger.info(f"Starting training pipeline: {n_txn} transactions, {f_ratio:.1%} fraud")

    # ---- Step 1: Generate data ----
    df = prepare_dataset(
        num_transactions=n_txn,
        fraud_ratio=f_ratio,
        save_dir="data/sample",
    )

    # ---- Step 2: Preprocess ----
    preprocessor = TransactionPreprocessor()
    splits = preprocessor.fit_transform(df)

    X_train = splits["X_train"]
    X_test = splits["X_test"]
    y_train = splits["y_train"]
    y_test = splits["y_test"]

    # ---- Step 3: Train models ----
    iso_model, iso_metrics = train_isolation_forest(X_train, X_test, y_test)
    lr_model, lr_metrics = train_logistic_regression(X_train, y_train, X_test, y_test)
    
    xgb_model = None
    xgb_metrics = {}
    if XGB_AVAILABLE:
        xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_test, y_test)

    # ---- Step 4: Save artifacts ----
    artifact_dir = Path(settings.MODEL_DIR)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    iso_path = artifact_dir / "isolation_forest.joblib"
    lr_path = artifact_dir / "logistic_regression.joblib"

    joblib.dump(iso_model, iso_path)
    joblib.dump(lr_model, lr_path)
    if xgb_model is not None:
        xgb_path = artifact_dir / "xgboost.joblib"
        joblib.dump(xgb_model, xgb_path)

    preprocessor.save(str(artifact_dir))

    # Save metrics
    metrics_path = artifact_dir / "training_metrics.json"
    all_metrics = {
        "isolation_forest": iso_metrics,
        "logistic_regression": lr_metrics,
        "feature_names": FEATURE_NAMES,
        "num_training_samples": int(X_train.shape[0]),
        "num_test_samples": int(X_test.shape[0]),
        "fraud_ratio": f_ratio,
    }
    if xgb_model is not None:
        all_metrics["xgboost"] = xgb_metrics

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    # Save LR coefficients for explainability
    coef_path = artifact_dir / "lr_coefficients.json"
    coefs = dict(zip(FEATURE_NAMES, lr_model.coef_[0].tolist()))
    with open(coef_path, "w", encoding="utf-8") as f:
        json.dump(coefs, f, indent=2)

    logger.info(f"All artifacts saved to {artifact_dir}")

    ret = {
        "artifact_dir": str(artifact_dir),
        "isolation_forest_metrics": iso_metrics,
        "logistic_regression_metrics": lr_metrics,
    }
    if xgb_model is not None:
        ret["xgboost_metrics"] = xgb_metrics
    return ret


if __name__ == "__main__":
    results = run_training_pipeline()
    print("\n✅ Training complete!")
    print(f"  Artifacts: {results['artifact_dir']}")
    print(f"  IF ROC-AUC: {results['isolation_forest_metrics']['roc_auc']:.4f}")
    print(f"  LR ROC-AUC: {results['logistic_regression_metrics']['roc_auc']:.4f}")
    if "xgboost_metrics" in results:
        print(f"  XGB ROC-AUC: {results['xgboost_metrics']['roc_auc']:.4f}")
