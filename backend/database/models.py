"""
Database operations for the Fraud Detection System.

Provides CRUD functions for transaction records and model metadata.
All operations are async to work with FastAPI's event loop.
"""

from datetime import datetime
from typing import Optional

import aiosqlite

from backend.database.connection import get_database
from utils.logger import get_logger

logger = get_logger(__name__)


async def store_transaction(
    transaction_id: str,
    transaction_data: dict,
    prediction_result: dict,
    explanation: str,
) -> None:
    """
    Store a transaction and its prediction result in the database.

    Args:
        transaction_id: Unique transaction identifier.
        transaction_data: Raw input features.
        prediction_result: Model prediction output.
        explanation: Human-readable explanation text.
    """
    db = await get_database()

    model_scores = prediction_result.get("model_scores", {})

    await db.execute(
        """
        INSERT OR REPLACE INTO transactions (
            transaction_id, amount, merchant_category,
            transaction_hour, day_of_week, location_distance_km,
            is_international, card_present, velocity_last_1h,
            avg_amount_30d, fraud_probability, risk_level,
            explanation, iso_score, lr_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction_id,
            transaction_data.get("amount", 0),
            transaction_data.get("merchant_category", "unknown"),
            transaction_data.get("transaction_hour", 0),
            transaction_data.get("day_of_week", 0),
            transaction_data.get("location_distance_km", 0),
            int(transaction_data.get("is_international", 0)),
            int(transaction_data.get("card_present", 1)),
            transaction_data.get("velocity_last_1h", 0),
            transaction_data.get("avg_amount_30d", 0),
            prediction_result["fraud_probability"],
            prediction_result["risk_level"],
            explanation,
            model_scores.get("isolation_forest_score"),
            model_scores.get("logistic_regression_score"),
        ),
    )
    await db.commit()
    logger.info(f"Transaction {transaction_id} stored in database")


async def get_transactions(
    limit: int = 50,
    offset: int = 0,
    risk_level: Optional[str] = None,
) -> list[dict]:
    """
    Retrieve stored transactions with optional filtering.

    Args:
        limit: Maximum number of records to return.
        offset: Number of records to skip (pagination).
        risk_level: Optional filter by risk level.

    Returns:
        List of transaction record dicts.
    """
    db = await get_database()

    if risk_level:
        cursor = await db.execute(
            """
            SELECT transaction_id, amount, merchant_category,
                   fraud_probability, risk_level, explanation, created_at
            FROM transactions
            WHERE risk_level = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (risk_level, limit, offset),
        )
    else:
        cursor = await db.execute(
            """
            SELECT transaction_id, amount, merchant_category,
                   fraud_probability, risk_level, explanation, created_at
            FROM transactions
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_stats() -> dict:
    """
    Compute aggregate statistics across all stored transactions.

    Returns:
        Dict with total counts, fraud rate, risk distribution, etc.
    """
    db = await get_database()

    # Total counts
    cursor = await db.execute("SELECT COUNT(*) as total FROM transactions")
    row = await cursor.fetchone()
    total = row["total"] if row else 0

    # Flagged (Medium or High)
    cursor = await db.execute(
        "SELECT COUNT(*) as flagged FROM transactions WHERE risk_level != 'Low'"
    )
    row = await cursor.fetchone()
    flagged = row["flagged"] if row else 0

    # Average fraud score
    cursor = await db.execute(
        "SELECT AVG(fraud_probability) as avg_score FROM transactions"
    )
    row = await cursor.fetchone()
    avg_score = row["avg_score"] if row and row["avg_score"] else 0.0

    # Risk distribution
    cursor = await db.execute(
        """
        SELECT risk_level, COUNT(*) as count
        FROM transactions
        GROUP BY risk_level
        """
    )
    risk_rows = await cursor.fetchall()
    risk_distribution = {row["risk_level"]: row["count"] for row in risk_rows}

    # Recent transactions
    recent = await get_transactions(limit=10)

    return {
        "total_transactions": total,
        "total_flagged": flagged,
        "fraud_rate": flagged / total if total > 0 else 0.0,
        "avg_fraud_score": round(avg_score, 4),
        "risk_distribution": risk_distribution,
        "recent_transactions": recent,
    }
