"""
Synthetic transaction data generator for the Fraud Detection System.

Generates realistic financial transaction data with configurable fraud patterns.
Fraud transactions exhibit statistically distinct behaviors:
    - Unusually high amounts
    - Odd-hour transactions (midnight – 5 AM)
    - International with card-not-present
    - High velocity (many transactions in a short window)
    - Large deviation from cardholder's average

Data Privacy Note:
    All data is 100% synthetic. No real customer, merchant, or card data is used.
    This aligns with PCI-DSS Requirement 3 (protect stored cardholder data)
    by ensuring no real cardholder data exists in the system.
"""

import numpy as np
import pandas as pd
from pathlib import Path

from utils.constants import (
    MERCHANT_CATEGORIES,
    DEFAULT_NUM_TRANSACTIONS,
    DEFAULT_FRAUD_RATIO,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_transactions(
    num_transactions: int = DEFAULT_NUM_TRANSACTIONS,
    fraud_ratio: float = DEFAULT_FRAUD_RATIO,
    random_seed: int = 42,
    save_path: str | None = None,
) -> pd.DataFrame:
    """
    Generate a synthetic transaction dataset with realistic fraud patterns.

    Args:
        num_transactions: Total number of transactions to generate.
        fraud_ratio: Proportion of transactions that are fraudulent (0.0–1.0).
        random_seed: Random seed for reproducibility.
        save_path: Optional file path to save the CSV.

    Returns:
        DataFrame with transaction features and fraud labels.
    """
    rng = np.random.default_rng(random_seed)

    num_fraud = int(num_transactions * fraud_ratio)
    num_legit = num_transactions - num_fraud

    logger.info(
        f"Generating {num_transactions} transactions "
        f"({num_fraud} fraud, {num_legit} legitimate)"
    )

    # ---- Generate legitimate transactions ----
    legit = _generate_legitimate(num_legit, rng)

    # ---- Generate fraudulent transactions ----
    fraud = _generate_fraudulent(num_fraud, rng)

    # ---- Combine and shuffle ----
    df = pd.concat([legit, fraud], ignore_index=True)
    df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    # Add transaction ID
    df.insert(0, "transaction_id", [f"TXN-{i:06d}" for i in range(len(df))])

    logger.info(f"Dataset generated: {df.shape[0]} rows, {df.shape[1]} columns")

    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        logger.info(f"Dataset saved to {path}")

    return df


def _generate_legitimate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate legitimate (non-fraudulent) transaction records."""
    return pd.DataFrame({
        "amount": rng.lognormal(mean=3.5, sigma=1.0, size=n).clip(0.50, 5000),
        "merchant_category": rng.choice(MERCHANT_CATEGORIES, size=n),
        "transaction_hour": rng.choice(range(6, 23), size=n),  # Mostly daytime
        "day_of_week": rng.integers(0, 7, size=n),
        "location_distance_km": rng.exponential(scale=5.0, size=n).clip(0, 50),
        "is_international": rng.choice([0, 1], size=n, p=[0.92, 0.08]),
        "card_present": rng.choice([0, 1], size=n, p=[0.15, 0.85]),
        "velocity_last_1h": rng.poisson(lam=1.2, size=n).clip(0, 5),
        "avg_amount_30d": rng.lognormal(mean=3.2, sigma=0.8, size=n).clip(5, 3000),
        "is_fraud": 0,
    })


def _generate_fraudulent(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generate fraudulent transaction records with distinct anomalous patterns.

    Fraud patterns modeled:
        1. High-value: amounts 5–50x above cardholder average
        2. Odd hours: midnight to 5 AM transactions
        3. International + card-not-present: common in CNP fraud
        4. Velocity spikes: many transactions in rapid succession
        5. Geographic anomaly: unusually far from home location
    """
    amounts = rng.lognormal(mean=5.5, sigma=1.5, size=n).clip(100, 50000)
    avg_amounts = amounts / rng.uniform(3, 15, size=n)  # Avg is much lower

    return pd.DataFrame({
        "amount": amounts,
        "merchant_category": rng.choice(
            ["electronics", "online_retail", "travel", "atm_withdrawal"],
            size=n,
            p=[0.3, 0.35, 0.2, 0.15],
        ),
        "transaction_hour": rng.choice(range(0, 6), size=n),  # Late night
        "day_of_week": rng.integers(0, 7, size=n),
        "location_distance_km": rng.uniform(50, 5000, size=n),  # Far away
        "is_international": rng.choice([0, 1], size=n, p=[0.3, 0.7]),
        "card_present": rng.choice([0, 1], size=n, p=[0.85, 0.15]),
        "velocity_last_1h": rng.poisson(lam=6, size=n).clip(3, 20),
        "avg_amount_30d": avg_amounts,
        "is_fraud": 1,
    })





def prepare_dataset(
    num_transactions: int = DEFAULT_NUM_TRANSACTIONS,
    fraud_ratio: float = DEFAULT_FRAUD_RATIO,
    save_dir: str | None = None,
) -> pd.DataFrame:
    """
    Full data preparation pipeline: generate → enrich → save.

    Args:
        num_transactions: Total transactions to generate.
        fraud_ratio: Fraction of fraud.
        save_dir: Directory to save the CSV file.

    Returns:
        Enriched DataFrame ready for model training.
    """
    df = generate_transactions(
        num_transactions=num_transactions,
        fraud_ratio=fraud_ratio,
        save_path=None,
    )

    if save_dir:
        save_path = Path(save_dir) / "transactions.csv"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)
        logger.info(f"Prepared dataset saved to {save_path}")

    return df


if __name__ == "__main__":
    # Quick-run: generate sample data
    df = prepare_dataset(save_dir="data/sample")
    print(f"\nDataset shape: {df.shape}")
    print(f"Fraud distribution:\n{df['is_fraud'].value_counts()}")
    print(f"\nSample:\n{df.head()}")
