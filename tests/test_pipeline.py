"""
End-to-end pipeline tests for the Fraud Detection System.

Tests the complete flow from data generation → training → inference.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generator import prepare_dataset
from data.preprocessor import TransactionPreprocessor
from models.train import train_isolation_forest, train_logistic_regression
from models.feature_engineering import engineer_features, extract_model_features
from models.explainability import explain_prediction
from utils.constants import FEATURE_NAMES


class TestEndToEndPipeline:
    """Test the complete pipeline from data to prediction."""

    @pytest.fixture(scope="class")
    def trained_pipeline(self, tmp_path_factory):
        """Train models on a small dataset for testing."""
        tmp_dir = tmp_path_factory.mktemp("artifacts")

        # Generate small dataset
        df = prepare_dataset(num_transactions=500, fraud_ratio=0.1)

        # Preprocess
        preprocessor = TransactionPreprocessor()
        splits = preprocessor.fit_transform(df)

        # Train both models
        iso_model, iso_metrics = train_isolation_forest(
            splits["X_train"], splits["X_test"], splits["y_test"]
        )
        lr_model, lr_metrics = train_logistic_regression(
            splits["X_train"], splits["y_train"],
            splits["X_test"], splits["y_test"],
        )

        # Save artifacts
        import joblib, json
        joblib.dump(iso_model, str(tmp_dir / "isolation_forest.joblib"))
        joblib.dump(lr_model, str(tmp_dir / "logistic_regression.joblib"))
        preprocessor.save(str(tmp_dir))

        coefs = dict(zip(FEATURE_NAMES, lr_model.coef_[0].tolist()))
        with open(str(tmp_dir / "lr_coefficients.json"), "w") as f:
            json.dump(coefs, f)

        return {
            "iso_model": iso_model,
            "lr_model": lr_model,
            "preprocessor": preprocessor,
            "iso_metrics": iso_metrics,
            "lr_metrics": lr_metrics,
            "artifact_dir": str(tmp_dir),
        }

    def test_isolation_forest_trains(self, trained_pipeline):
        assert trained_pipeline["iso_model"] is not None

    def test_logistic_regression_trains(self, trained_pipeline):
        assert trained_pipeline["lr_model"] is not None

    def test_iso_metrics_reasonable(self, trained_pipeline):
        metrics = trained_pipeline["iso_metrics"]
        # ROC-AUC should be better than random (0.5)
        assert metrics["roc_auc"] > 0.5

    def test_lr_metrics_reasonable(self, trained_pipeline):
        metrics = trained_pipeline["lr_metrics"]
        assert metrics["roc_auc"] > 0.7  # LR should do well on synthetic data

    def test_inference_on_normal_transaction(self, trained_pipeline):
        """Test that a normal transaction gets a reasonable score."""
        data = {
            "amount": 45.0,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 3.0,
            "is_international": 0,
            "card_present": 1,
            "velocity_last_1h": 1,
            "avg_amount_30d": 52.0,
        }

        df = engineer_features(data)
        X = extract_model_features(df)
        X_scaled = trained_pipeline["preprocessor"].scaler.transform(X)

        # LR prediction
        proba = trained_pipeline["lr_model"].predict_proba(X_scaled)[0][1]
        # Normal transaction should have low fraud probability
        assert proba < 0.7  # Should be low risk

    def test_inference_on_fraudulent_transaction(self, trained_pipeline):
        """Test that a suspicious transaction gets a higher score."""
        data = {
            "amount": 4999.0,
            "merchant_category": "online_retail",
            "transaction_hour": 2,
            "day_of_week": 6,
            "location_distance_km": 3500.0,
            "is_international": 1,
            "card_present": 0,
            "velocity_last_1h": 12,
            "avg_amount_30d": 65.0,
        }

        df = engineer_features(data)
        X = extract_model_features(df)
        X_scaled = trained_pipeline["preprocessor"].scaler.transform(X)

        # LR prediction
        proba = trained_pipeline["lr_model"].predict_proba(X_scaled)[0][1]
        # Suspicious transaction should have higher fraud probability
        assert proba > 0.3  # Should be at least medium risk

    def test_explainability_output(self, trained_pipeline):
        """Test that explanation generation works."""
        feature_values = {
            "amount": 4999.0,
            "merchant_category_encoded": 4,
            "transaction_hour": 2,
            "day_of_week": 6,
            "location_distance_km": 3500.0,
            "is_international": 1,
            "card_present": 0,
            "velocity_last_1h": 12,
            "avg_amount_30d": 65.0,
            "amount_deviation": 75.9,
        }

        explanation = explain_prediction(
            feature_values=feature_values,
            model_dir=trained_pipeline["artifact_dir"],
            top_n=3,
        )

        assert "explanation_text" in explanation
        assert "top_factors" in explanation
        assert "contributions" in explanation
        assert len(explanation["top_factors"]) <= 3
        assert len(explanation["explanation_text"]) > 10  # Non-trivial text
