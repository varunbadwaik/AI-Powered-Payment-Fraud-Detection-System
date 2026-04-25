"""
SQLite database connection manager for the Fraud Detection System.

Uses aiosqlite for async operations to avoid blocking the FastAPI event loop.
Connection is managed as a module-level singleton with auto-table-creation.

PCI-DSS Requirement 3 Note:
    This database stores only synthetic transaction data and fraud scores.
    No real cardholder data (PAN, CVV, expiry) is ever persisted.
"""

import aiosqlite
from pathlib import Path

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level connection reference
_db_connection: aiosqlite.Connection | None = None


async def get_database() -> aiosqlite.Connection:
    """
    Get or create the singleton database connection.

    Returns:
        Active aiosqlite connection.
    """
    global _db_connection
    if _db_connection is None:
        db_path = Path(settings.DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _db_connection = await aiosqlite.connect(str(db_path))
        _db_connection.row_factory = aiosqlite.Row
        await _initialize_tables(_db_connection)
        logger.info(f"Database connected: {db_path}")
    return _db_connection


async def _initialize_tables(db: aiosqlite.Connection) -> None:
    """Create tables if they don't exist."""
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            merchant_category TEXT NOT NULL,
            transaction_hour INTEGER NOT NULL,
            day_of_week INTEGER DEFAULT 0,
            location_distance_km REAL DEFAULT 0.0,
            is_international INTEGER DEFAULT 0,
            card_present INTEGER DEFAULT 1,
            velocity_last_1h INTEGER DEFAULT 0,
            avg_amount_30d REAL DEFAULT 0.0,
            fraud_probability REAL NOT NULL,
            risk_level TEXT NOT NULL,
            explanation TEXT,
            iso_score REAL,
            lr_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_version TEXT NOT NULL,
            training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_training_samples INTEGER,
            roc_auc REAL,
            precision_fraud REAL,
            recall_fraud REAL,
            f1_fraud REAL
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_risk
            ON transactions(risk_level);
        CREATE INDEX IF NOT EXISTS idx_transactions_created
            ON transactions(created_at);
    """)
    await db.commit()
    logger.info("Database tables initialized")


async def close_database() -> None:
    """Close the database connection gracefully."""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None
        logger.info("Database connection closed")
