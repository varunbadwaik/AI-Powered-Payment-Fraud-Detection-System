"""
Advanced feature engineering module for the Fraud Detection System.

Transforms raw transaction data into a 22-feature ML-ready vector.
Adds behavioral Z-scores, velocity ratios, geographic anomaly scores,
merchant risk encoding, and cross-feature interaction terms.

Feature Groups:
    - Base (10): raw + simple encodings
    - Behavioral (4): amount_zscore, amount_to_avg_ratio, velocity_ratio, risk_composite
    - Interaction (3): amount×velocity, distance×velocity, CNP+international
    - Categorical Risk (3): high-risk merchant, high-risk hour, high velocity
    - Anomaly Signals (2): round amount flag, distance risk score
"""

import numpy as np
import pandas as pd

from utils.constants import (
    MERCHANT_CATEGORY_MAP,
    MERCHANT_RISK_HIGH,
    FEATURE_NAMES,
    HIGH_VELOCITY_THRESHOLD,
    VELOCITY_SPIKE_MULTIPLIER,
    DISTANCE_NORMALIZATION_KM,
    AVG_VELOCITY_BASELINE,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def engineer_features(data: dict | pd.DataFrame) -> pd.DataFrame:
    """
    Apply full feature engineering pipeline to raw transaction data.

    Accepts either a single transaction dict (API request)
    or a full DataFrame (batch training).

    Args:
        data: Raw transaction data as dict or DataFrame.

    Returns:
        DataFrame with all 22 engineered features ready for model input.
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()

    # ── Stage 1: Base encodings ──────────────────────────────────────
    _encode_merchant_category(df)
    _compute_amount_deviation(df)

    # ── Stage 2: Behavioral Z-scores & ratios ────────────────────────
    _compute_amount_zscore(df)
    _compute_amount_to_avg_ratio(df)
    _compute_velocity_ratio(df)

    # ── Stage 3: Interaction features ────────────────────────────────
    _compute_amount_velocity_product(df)
    _compute_distance_velocity_interaction(df)
    _compute_cnp_international(df)

    # ── Stage 4: Categorical risk flags ──────────────────────────────
    _compute_high_risk_merchant(df)
    _compute_high_risk_hour(df)
    _compute_high_velocity_flag(df)

    # ── Stage 5: Anomaly signals ─────────────────────────────────────
    _compute_round_amount_flag(df)
    _compute_distance_risk_score(df)

    # ── Stage 6: Pre-ML risk composite ───────────────────────────────
    _compute_risk_composite(df)

    return df


# ======================================================================
#  Stage 1: Base Encodings
# ======================================================================

def _encode_merchant_category(df: pd.DataFrame) -> None:
    """Encode merchant_category string to integer."""
    if "merchant_category" in df.columns and "merchant_category_encoded" not in df.columns:
        df["merchant_category_encoded"] = (
            df["merchant_category"]
            .map(MERCHANT_CATEGORY_MAP)
            .fillna(-1)
            .astype(int)
        )


def _compute_amount_deviation(df: pd.DataFrame) -> None:
    """Percentage deviation from 30-day average: (amount - avg) / avg."""
    if "amount_deviation" not in df.columns:
        df["amount_deviation"] = np.where(
            df["avg_amount_30d"] > 0,
            (df["amount"] - df["avg_amount_30d"]) / df["avg_amount_30d"],
            0.0,
        )


# ======================================================================
#  Stage 2: Behavioral Z-Scores & Ratios
# ======================================================================

def _compute_amount_zscore(df: pd.DataFrame) -> None:
    """
    Approximate Z-score of the transaction amount relative to user history.

    Uses avg_amount_30d as mean and estimates std as avg * 0.5
    (conservative assumption when true std is unavailable).
    """
    if "amount_zscore" not in df.columns:
        estimated_std = df["avg_amount_30d"] * 0.5
        estimated_std = estimated_std.replace(0, 1)  # avoid div-by-zero
        df["amount_zscore"] = (
            (df["amount"] - df["avg_amount_30d"]) / estimated_std
        ).clip(-10, 10)


def _compute_amount_to_avg_ratio(df: pd.DataFrame) -> None:
    """How many multiples of the user's average is this transaction."""
    if "amount_to_avg_ratio" not in df.columns:
        df["amount_to_avg_ratio"] = np.where(
            df["avg_amount_30d"] > 0,
            df["amount"] / df["avg_amount_30d"],
            1.0,
        ).clip(0, 100)


def _compute_velocity_ratio(df: pd.DataFrame) -> None:
    """
    Ratio of current velocity to baseline expected velocity.

    velocity_ratio > 3 indicates a suspicious spike.
    """
    if "velocity_ratio" not in df.columns:
        df["velocity_ratio"] = (
            df["velocity_last_1h"] / AVG_VELOCITY_BASELINE
        ).clip(0, 50)


# ======================================================================
#  Stage 3: Interaction Features
# ======================================================================

def _compute_amount_velocity_product(df: pd.DataFrame) -> None:
    """
    Combined spend-velocity signal: high amount AND high frequency.

    Normalized by log1p to prevent extreme values from dominating.
    """
    if "amount_velocity_product" not in df.columns:
        df["amount_velocity_product"] = np.log1p(
            df["amount"] * df["velocity_last_1h"]
        )


def _compute_distance_velocity_interaction(df: pd.DataFrame) -> None:
    """
    Impossible-travel detection: far distance + rapid transactions.

    High values suggest the cardholder couldn't physically be at both locations.
    """
    if "distance_velocity_interaction" not in df.columns:
        df["distance_velocity_interaction"] = np.log1p(
            df["location_distance_km"] * df["velocity_last_1h"]
        )


def _compute_cnp_international(df: pd.DataFrame) -> None:
    """Card-not-present AND international: highest-risk combination in CNP fraud."""
    if "card_not_present_international" not in df.columns:
        df["card_not_present_international"] = (
            (1 - df["card_present"].astype(int)) * df["is_international"].astype(int)
        ).astype(int)


# ======================================================================
#  Stage 4: Categorical Risk Flags
# ======================================================================

def _compute_high_risk_merchant(df: pd.DataFrame) -> None:
    """Flag merchants in the high-risk category tier."""
    if "is_high_risk_merchant" not in df.columns:
        if "merchant_category" in df.columns:
            df["is_high_risk_merchant"] = (
                df["merchant_category"].isin(MERCHANT_RISK_HIGH)
            ).astype(int)
        else:
            df["is_high_risk_merchant"] = 0


def _compute_high_risk_hour(df: pd.DataFrame) -> None:
    """Extended night window: 10 PM – 5 AM (hours 0-5, 22-23)."""
    if "is_high_risk_hour" not in df.columns:
        hour = df["transaction_hour"]
        df["is_high_risk_hour"] = (
            ((hour >= 0) & (hour <= 5)) | ((hour >= 22) & (hour <= 23))
        ).astype(int)


def _compute_high_velocity_flag(df: pd.DataFrame) -> None:
    """Binary flag when velocity exceeds the suspicious threshold."""
    if "is_high_velocity" not in df.columns:
        df["is_high_velocity"] = (
            df["velocity_last_1h"] > HIGH_VELOCITY_THRESHOLD
        ).astype(int)


# ======================================================================
#  Stage 5: Anomaly Signals
# ======================================================================

def _compute_round_amount_flag(df: pd.DataFrame) -> None:
    """
    Fraudsters often use round amounts (100, 500, 1000).
    Flag amounts that are exact multiples of 100.
    """
    if "is_round_amount" not in df.columns:
        df["is_round_amount"] = (
            (df["amount"] >= 100) & (df["amount"] % 100 == 0)
        ).astype(int)


def _compute_distance_risk_score(df: pd.DataFrame) -> None:
    """Normalized 0-1 geographic risk score: distance / normalization_factor."""
    if "distance_risk_score" not in df.columns:
        df["distance_risk_score"] = (
            df["location_distance_km"] / DISTANCE_NORMALIZATION_KM
        ).clip(0, 1)


# ======================================================================
#  Stage 6: Pre-ML Risk Composite
# ======================================================================

def _compute_risk_composite(df: pd.DataFrame) -> None:
    """
    Weighted pre-ML risk aggregation combining multiple signals.

    This is NOT the final fraud score — it's a feature that helps
    the ML models by providing a hand-crafted risk summary.

    Weights are tuned heuristically:
        - amount deviation:   25%
        - distance risk:      20%
        - velocity ratio:     20%
        - high-risk hour:     10%
        - high-risk merchant: 10%
        - CNP+international:  15%
    """
    if "risk_composite" not in df.columns:
        # Normalize amount_deviation to 0-1 range
        norm_deviation = (df["amount_deviation"].clip(0, 10) / 10)

        df["risk_composite"] = (
            0.25 * norm_deviation
            + 0.20 * df.get("distance_risk_score", 0)
            + 0.20 * (df.get("velocity_ratio", 0) / 50).clip(0, 1)
            + 0.10 * df.get("is_high_risk_hour", 0)
            + 0.10 * df.get("is_high_risk_merchant", 0)
            + 0.15 * df.get("card_not_present_international", 0)
        ).clip(0, 1)


# ======================================================================
#  Extraction Helpers
# ======================================================================

def extract_model_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract the canonical 22-feature vector expected by trained models.

    Args:
        df: DataFrame with engineered features.

    Returns:
        2D numpy array with columns in FEATURE_NAMES order.
    """
    missing = [f for f in FEATURE_NAMES if f not in df.columns]
    if missing:
        raise ValueError(
            f"Missing features after engineering: {missing}. "
            f"Available: {list(df.columns)}"
        )

    return df[FEATURE_NAMES].values.astype(np.float64)


def get_feature_values_for_explanation(
    data: dict,
) -> dict[str, float]:
    """
    Return a clean dict of feature name → value for explainability.
    Used to show the user which feature values drove the prediction.

    Args:
        data: Single transaction dictionary.

    Returns:
        Dict mapping feature display names to their values.
    """
    df = engineer_features(data)
    row = df.iloc[0]

    return {feat: float(row[feat]) for feat in FEATURE_NAMES if feat in row.index}
