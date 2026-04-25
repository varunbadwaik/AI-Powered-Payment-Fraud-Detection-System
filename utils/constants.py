"""
Project-wide constants for the AI-Powered Payment Fraud Detection System.

All thresholds, feature definitions, and enumerations are centralized here
to avoid hardcoding values throughout the codebase.
"""

# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------
API_VERSION = "2.0.0"
MODEL_VERSION = "2.0.0"

# ---------------------------------------------------------------------------
# Risk Thresholds  (overridable via config/fraud_thresholds.yaml)
# ---------------------------------------------------------------------------
RISK_THRESHOLD_LOW = 0.3
RISK_THRESHOLD_HIGH = 0.7

RISK_LEVEL_LOW = "Low"
RISK_LEVEL_MEDIUM = "Medium"
RISK_LEVEL_HIGH = "High"

# ---------------------------------------------------------------------------
# Merchant Categories
# ---------------------------------------------------------------------------
MERCHANT_CATEGORIES = [
    "grocery",
    "electronics",
    "restaurant",
    "gas_station",
    "online_retail",
    "travel",
    "entertainment",
    "healthcare",
    "utilities",
    "atm_withdrawal",
]

MERCHANT_CATEGORY_MAP = {cat: idx for idx, cat in enumerate(MERCHANT_CATEGORIES)}

# Merchant risk tiers — used by feature engineering
MERCHANT_RISK_HIGH = {"electronics", "online_retail", "atm_withdrawal", "travel"}
MERCHANT_RISK_MEDIUM = {"entertainment", "gas_station"}
MERCHANT_RISK_LOW = {"grocery", "restaurant", "healthcare", "utilities"}

# ---------------------------------------------------------------------------
# Feature Definitions — order matters for model input
# ---------------------------------------------------------------------------
# Original raw features (10)
BASE_FEATURE_NAMES = [
    "amount",
    "merchant_category_encoded",
    "transaction_hour",
    "day_of_week",
    "location_distance_km",
    "is_international",
    "card_present",
    "velocity_last_1h",
    "avg_amount_30d",
    "amount_deviation",
]

# Advanced engineered features (12 new)
ENGINEERED_FEATURE_NAMES = [
    "amount_zscore",
    "amount_to_avg_ratio",
    "velocity_ratio",
    "amount_velocity_product",
    "distance_velocity_interaction",
    "is_high_risk_merchant",
    "is_high_risk_hour",
    "is_round_amount",
    "distance_risk_score",
    "is_high_velocity",
    "card_not_present_international",
    "risk_composite",
]

# Full canonical feature list (22 features total)
FEATURE_NAMES = BASE_FEATURE_NAMES + ENGINEERED_FEATURE_NAMES

FEATURE_DISPLAY_NAMES = {
    # Base features
    "amount": "Transaction Amount ($)",
    "merchant_category_encoded": "Merchant Category",
    "transaction_hour": "Hour of Day",
    "day_of_week": "Day of Week",
    "location_distance_km": "Distance from Home (km)",
    "is_international": "International Transaction",
    "card_present": "Card Present",
    "velocity_last_1h": "Transactions in Last Hour",
    "avg_amount_30d": "30-Day Avg Amount ($)",
    "amount_deviation": "Amount Deviation from Avg",
    # Engineered features
    "amount_zscore": "Amount Z-Score",
    "amount_to_avg_ratio": "Amount / Avg Ratio",
    "velocity_ratio": "Velocity Spike Ratio",
    "amount_velocity_product": "Amount × Velocity",
    "distance_velocity_interaction": "Distance × Velocity",
    "is_high_risk_merchant": "High-Risk Merchant",
    "is_high_risk_hour": "High-Risk Hour",
    "is_round_amount": "Round Amount Flag",
    "distance_risk_score": "Geographic Risk Score",
    "is_high_velocity": "High Velocity Flag",
    "card_not_present_international": "CNP + International",
    "risk_composite": "Pre-ML Risk Composite",
}

# ---------------------------------------------------------------------------
# Feature Engineering Thresholds
# ---------------------------------------------------------------------------
HIGH_VELOCITY_THRESHOLD = 5       # txns/hour considered "high"
AMOUNT_SPIKE_MULTIPLIER = 10      # 10x avg = spike
VELOCITY_SPIKE_MULTIPLIER = 3     # 3x normal velocity = spike
DISTANCE_NORMALIZATION_KM = 500   # distance / 500 for 0-1 score
AVG_VELOCITY_BASELINE = 2.0       # assumed baseline txns/hour for ratio

# ---------------------------------------------------------------------------
# Data Generation Defaults
# ---------------------------------------------------------------------------
DEFAULT_NUM_TRANSACTIONS = 10_000
DEFAULT_FRAUD_RATIO = 0.03  # 3% — realistic imbalance

# ---------------------------------------------------------------------------
# Model Training Defaults
# ---------------------------------------------------------------------------
ISOLATION_FOREST_PARAMS = {
    "n_estimators": 200,
    "max_samples": "auto",
    "contamination": DEFAULT_FRAUD_RATIO,
    "random_state": 42,
    "n_jobs": -1,
}

LOGISTIC_REGRESSION_PARAMS = {
    "class_weight": "balanced",
    "max_iter": 1000,
    "random_state": 42,
    "solver": "lbfgs",
}

XGBOOST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.1,
    "scale_pos_weight": int(1 / DEFAULT_FRAUD_RATIO),  # ~33 for 3% fraud
    "random_state": 42,
    "eval_metric": "aucpr",
    "use_label_encoder": False,
}

# ---------------------------------------------------------------------------
# Default Ensemble Weights
# ---------------------------------------------------------------------------
DEFAULT_ENSEMBLE_WEIGHTS = {
    "isolation_forest": 0.25,
    "logistic_regression": 0.45,
    "xgboost": 0.30,
}

# Fallback when XGBoost is not available
FALLBACK_ENSEMBLE_WEIGHTS = {
    "isolation_forest": 0.40,
    "logistic_regression": 0.60,
}

# ---------------------------------------------------------------------------
# API Defaults
# ---------------------------------------------------------------------------
DEFAULT_API_HOST = "0.0.0.0"
DEFAULT_API_PORT = 8000
DEFAULT_DB_PATH = "data/fraud_detection.db"
DEFAULT_MODEL_DIR = "models/artifacts"

# ---------------------------------------------------------------------------
# PCI-DSS Reference Notes (Awareness — NOT a full implementation)
# ---------------------------------------------------------------------------
# PCI-DSS Requirement 3: Protect stored cardholder data
#   - This system does NOT store real PANs, CVVs, or sensitive auth data.
#   - All transaction data is synthetic / simulated.
# PCI-DSS Requirement 6: Develop and maintain secure systems
#   - Input validation on all API endpoints (Pydantic).
#   - Error messages do not leak internal details.
# PCI-DSS Requirement 10: Track and monitor access
#   - Structured logging for all prediction requests.
