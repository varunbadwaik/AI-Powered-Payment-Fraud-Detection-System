"""
ML model tests for the Fraud Detection System.

Tests data generation, preprocessing, training, and inference.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generator import generate_transactions, prepare_dataset
from data.preprocessor import TransactionPreprocessor
from models.feature_engineering import engineer_features, extract_model_features
from utils.constants import FEATURE_NAMES, MERCHANT_CATEGORIES


class TestDataGeneration:
    """Tests for synthetic data generation."""

    def test_generates_correct_count(self):
        df = generate_transactions(num_transactions=100)
        assert len(df) == 100

    def test_has_fraud_label(self):
        df = generate_transactions(num_transactions=100)
        assert "is_fraud" in df.columns
        assert set(df["is_fraud"].unique()).issubset({0, 1})

    def test_fraud_ratio_approximate(self):
        df = generate_transactions(num_transactions=1000, fraud_ratio=0.1)
        actual_ratio = df["is_fraud"].mean()
        assert 0.05 <= actual_ratio <= 0.15  # Allow some variance

    def test_has_required_columns(self):
        df = generate_transactions(num_transactions=100)
        required = ["amount", "merchant_category", "transaction_hour",
                     "is_international", "card_present", "velocity_last_1h"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_merchant_categories_valid(self):
        df = generate_transactions(num_transactions=100)
        for cat in df["merchant_category"].unique():
            assert cat in MERCHANT_CATEGORIES

    def test_amounts_positive(self):
        df = generate_transactions(num_transactions=100)
        assert (df["amount"] > 0).all()

    def test_transaction_hours_valid(self):
        df = generate_transactions(num_transactions=100)
        assert (df["transaction_hour"] >= 0).all()
        assert (df["transaction_hour"] <= 23).all()


class TestPreprocessor:
    """Tests for the data preprocessor."""

    @pytest.fixture
    def sample_df(self):
        return prepare_dataset(num_transactions=500, fraud_ratio=0.1)

    def test_fit_transform_returns_splits(self, sample_df):
        preprocessor = TransactionPreprocessor()
        splits = preprocessor.fit_transform(sample_df)
        assert "X_train" in splits
        assert "X_test" in splits
        assert "y_train" in splits
        assert "y_test" in splits

    def test_correct_feature_count(self, sample_df):
        preprocessor = TransactionPreprocessor()
        splits = preprocessor.fit_transform(sample_df)
        assert splits["X_train"].shape[1] == len(FEATURE_NAMES)

    def test_split_preserves_total(self, sample_df):
        preprocessor = TransactionPreprocessor()
        splits = preprocessor.fit_transform(sample_df)
        total = splits["X_train"].shape[0] + splits["X_test"].shape[0]
        assert total == len(sample_df)

    def test_scaler_normalizes(self, sample_df):
        preprocessor = TransactionPreprocessor()
        splits = preprocessor.fit_transform(sample_df)
        # After scaling, mean should be near 0
        mean = np.abs(splits["X_train"].mean(axis=0)).mean()
        assert mean < 1.0  # Scaled data has small mean

    def test_save_and_load(self, sample_df, tmp_path):
        preprocessor = TransactionPreprocessor()
        preprocessor.fit_transform(sample_df)
        preprocessor.save(str(tmp_path))

        new_preprocessor = TransactionPreprocessor()
        new_preprocessor.load(str(tmp_path))
        assert new_preprocessor._is_fitted


class TestFeatureEngineering:
    """Tests for feature engineering functions."""

    def test_engineer_from_dict(self):
        data = {
            "amount": 100.0,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 5.0,
            "is_international": 0,
            "card_present": 1,
            "velocity_last_1h": 1,
            "avg_amount_30d": 85.0,
        }
        df = engineer_features(data)
        assert len(df) == 1
        assert "merchant_category_encoded" in df.columns
        assert "amount_zscore" in df.columns

    def test_engineer_from_dataframe(self):
        df = pd.DataFrame([{
            "amount": 100.0,
            "merchant_category": "electronics",
            "transaction_hour": 22,
            "day_of_week": 5,
            "location_distance_km": 100.0,
            "is_international": 1,
            "card_present": 0,
            "velocity_last_1h": 5,
            "avg_amount_30d": 50.0,
        }])
        result = engineer_features(df)
        assert "is_high_risk_hour" in result.columns
        assert "is_high_risk_merchant" in result.columns

    def test_extract_model_features_shape(self):
        data = {
            "amount": 100.0,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 5.0,
            "is_international": 0,
            "card_present": 1,
            "velocity_last_1h": 1,
            "avg_amount_30d": 85.0,
        }
        df = engineer_features(data)
        X = extract_model_features(df)
        assert X.shape == (1, len(FEATURE_NAMES))

    def test_amount_deviation_calculation(self):
        data = {
            "amount": 200.0,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 5.0,
            "is_international": 0,
            "card_present": 1,
            "velocity_last_1h": 1,
            "avg_amount_30d": 100.0,
        }
        df = engineer_features(data)
        # (200 - 100) / 100 = 1.0
        assert abs(df.iloc[0]["amount_deviation"] - 1.0) < 0.01
