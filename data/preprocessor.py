"""
Data preprocessing pipeline for the Fraud Detection System.

Handles:
    - Feature selection and ordering
    - Categorical encoding (merchant category)
    - Numerical scaling (StandardScaler)
    - Stratified train/test splitting
    - Scaler persistence for inference-time consistency

Data Privacy Note:
    Preprocessing operates on synthetic data only.
    No real PII is transformed or stored.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from models.feature_engineering import engineer_features, extract_model_features
from utils.constants import FEATURE_NAMES
from utils.logger import get_logger

logger = get_logger(__name__)


class TransactionPreprocessor:
    """
    Stateful preprocessor that fits a scaler on training data
    and can transform new data consistently.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self._is_fitted = False

    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract the feature matrix from a DataFrame in the canonical feature order.
        Uses the shared feature_engineering module to ensure training/inference parity.

        Args:
            df: DataFrame with raw or partially processed columns.

        Returns:
            2D numpy array of shape (n_samples, n_features).
        """
        # Apply full feature engineering pipeline
        df_engineered = engineer_features(df)
        
        # Extract the correct 22-feature array
        return extract_model_features(df_engineered)

    def fit_transform(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> dict:
        """
        Full preprocessing pipeline: encode → extract → split → scale.

        Args:
            df: Raw transaction DataFrame (must contain 'is_fraud' column).
            test_size: Fraction reserved for testing.
            random_state: Seed for reproducible splits.

        Returns:
            Dictionary with keys: X_train, X_test, y_train, y_test
        """
        logger.info("Starting fit_transform pipeline")

        X = self.extract_features(df)
        y = df["is_fraud"].values

        # Stratified split to preserve fraud ratio in both sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, stratify=y, random_state=random_state
        )

        # Fit scaler on training data only (prevent data leakage)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        self._is_fitted = True

        logger.info(
            f"Split complete: train={X_train.shape[0]}, test={X_test.shape[0]}"
        )

        return {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform new data using the already-fitted scaler.

        Used at inference time to preprocess incoming API requests.

        Args:
            df: DataFrame with transaction features.

        Returns:
            Scaled feature array.

        Raises:
            RuntimeError: If scaler has not been fitted.
        """
        if not self._is_fitted:
            raise RuntimeError(
                "Preprocessor has not been fitted. "
                "Call fit_transform() first or load a saved scaler."
            )

        X = self.extract_features(df)
        return self.scaler.transform(X)

    def save(self, directory: str) -> None:
        """Persist the fitted scaler to disk."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        scaler_path = path / "scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")

    def load(self, directory: str) -> None:
        """Load a previously fitted scaler from disk."""
        scaler_path = Path(directory) / "scaler.joblib"
        if not scaler_path.exists():
            raise FileNotFoundError(f"No scaler found at {scaler_path}")
        self.scaler = joblib.load(scaler_path)
        self._is_fitted = True
        logger.info(f"Scaler loaded from {scaler_path}")
