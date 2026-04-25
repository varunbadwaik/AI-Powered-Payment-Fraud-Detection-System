"""
Explainability module for the Fraud Detection System.

Provides both per-prediction explanations and global feature importance.

Approach:
    - Logistic Regression coefficients → global feature importance.
    - Per-prediction: identify which features contributed most to the score
      by examining (coefficient × feature_value) products.
    - Human-readable explanation strings for dashboard display.

This is a lightweight, model-intrinsic explainability approach.
For production systems, consider SHAP or LIME for model-agnostic explanations.
"""

import json
from pathlib import Path

import numpy as np

from utils.constants import FEATURE_NAMES, FEATURE_DISPLAY_NAMES
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def get_global_feature_importance(model_dir: str | None = None) -> dict[str, float]:
    """
    Load global feature importance from saved LR coefficients.

    The absolute value of each coefficient indicates how much that feature
    contributes to fraud classification.

    Args:
        model_dir: Path to model artifacts.

    Returns:
        Dict of feature_name → importance_score, sorted by importance.
    """
    artifact_dir = Path(model_dir or settings.MODEL_DIR)
    coef_path = artifact_dir / "lr_coefficients.json"

    if not coef_path.exists():
        logger.warning("LR coefficients file not found — returning empty importance")
        return {}

    with open(coef_path, "r") as f:
        coefficients = json.load(f)

    # Use absolute values for importance magnitude
    importance = {
        FEATURE_DISPLAY_NAMES.get(k, k): abs(v)
        for k, v in coefficients.items()
    }

    # Sort by importance (descending)
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    return importance


def explain_prediction(
    feature_values: dict[str, float],
    model_dir: str | None = None,
    top_n: int = 3,
) -> dict:
    """
    Generate a per-prediction explanation for why a transaction was flagged.

    Computes `contribution = coefficient × feature_value` for each feature
    to determine which features drove the fraud score.

    Args:
        feature_values: Dict mapping FEATURE_NAMES → values (from inference).
        model_dir: Path to model artifacts.
        top_n: Number of top contributing features to highlight.

    Returns:
        Dict with:
            - contributions: full dict of feature → contribution score
            - top_factors: list of top N contributing factors
            - explanation_text: human-readable explanation string
    """
    artifact_dir = Path(model_dir or settings.MODEL_DIR)
    coef_path = artifact_dir / "lr_coefficients.json"

    if not coef_path.exists():
        return {
            "contributions": {},
            "top_factors": [],
            "explanation_text": "Explanation unavailable — model coefficients not found.",
        }

    with open(coef_path, "r") as f:
        coefficients = json.load(f)

    # Compute per-feature contribution to fraud score
    contributions = {}
    for feat_name in FEATURE_NAMES:
        coef = coefficients.get(feat_name, 0.0)
        value = feature_values.get(feat_name, 0.0)
        contribution = coef * value
        display_name = FEATURE_DISPLAY_NAMES.get(feat_name, feat_name)
        contributions[display_name] = round(contribution, 4)

    # Sort by absolute contribution (most influential first)
    sorted_contributions = sorted(
        contributions.items(), key=lambda x: abs(x[1]), reverse=True
    )

    top_factors = sorted_contributions[:top_n]

    # Generate human-readable explanation
    explanation_parts = []
    for feat_display, contrib in top_factors:
        feat_key = next(
            (k for k, v in FEATURE_DISPLAY_NAMES.items() if v == feat_display),
            feat_display,
        )
        value = feature_values.get(feat_key, 0)
        direction = "increased" if contrib > 0 else "decreased"

        explanation_parts.append(
            _make_explanation_sentence(feat_display, value, direction, feat_key)
        )

    explanation_text = " ".join(explanation_parts) if explanation_parts else (
        "No significant risk factors detected."
    )

    return {
        "contributions": dict(sorted_contributions),
        "top_factors": [
            {"feature": f, "contribution": c} for f, c in top_factors
        ],
        "explanation_text": explanation_text,
    }


def _make_explanation_sentence(
    feature_display: str,
    value: float,
    direction: str,
    feature_key: str,
) -> str:
    """
    Generate a contextual explanation sentence for a single feature.

    Returns human-friendly text like:
        "The transaction amount of $3,200 is unusually high, increasing fraud risk."
    """
    templates = {
        "amount": (
            f"The transaction amount of ${value:,.2f} "
            f"{'is unusually high' if direction == 'increased' else 'is within normal range'}, "
            f"{'increasing' if direction == 'increased' else 'decreasing'} fraud risk."
        ),
        "transaction_hour": (
            f"The transaction occurred at hour {int(value)} "
            f"({'late night/early morning' if value < 6 else 'regular hours'}), "
            f"which {direction} the risk score."
        ),
        "location_distance_km": (
            f"The transaction location is {value:.0f} km from the cardholder's typical area, "
            f"which {direction} the risk score."
        ),
        "is_international": (
            f"This {'is' if value == 1 else 'is not'} an international transaction, "
            f"which {direction} the risk score."
        ),
        "card_present": (
            f"The card was {'present' if value == 1 else 'not present'} at the point of sale, "
            f"which {direction} the risk score."
        ),
        "velocity_last_1h": (
            f"There were {int(value)} transactions in the last hour, "
            f"which {direction} the risk score."
        ),
        "amount_deviation": (
            f"The amount deviates {value:.1%} from the 30-day average, "
            f"which {direction} the risk score."
        ),
        "avg_amount_30d": (
            f"The cardholder's 30-day average is ${value:,.2f}, "
            f"and the current transaction {direction} the risk score."
        ),
        "merchant_category_encoded": (
            f"The merchant category (code {int(value)}) "
            f"{direction} the risk score."
        ),
        "day_of_week": (
            f"The transaction day (day {int(value)}) "
            f"{direction} the risk score."
        ),
    }

    return templates.get(
        feature_key,
        f"{feature_display} (value: {value:.2f}) {direction} the risk score.",
    )
