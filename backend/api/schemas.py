"""
Pydantic schemas for API request/response validation.

All inputs are strictly validated to prevent injection attacks
and ensure data integrity. Error messages are informative but
do not leak internal system details (PCI-DSS Requirement 6).
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationInfo

from utils.constants import MERCHANT_CATEGORIES


class MerchantCategory(str, Enum):
    """Valid merchant categories for transaction classification."""
    GROCERY = "grocery"
    ELECTRONICS = "electronics"
    RESTAURANT = "restaurant"
    GAS_STATION = "gas_station"
    ONLINE_RETAIL = "online_retail"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    UTILITIES = "utilities"
    ATM_WITHDRAWAL = "atm_withdrawal"


class TransactionRequest(BaseModel):
    """
    Input schema for a single transaction to be evaluated for fraud.

    All fields have validation constraints to ensure data quality
    and prevent abuse of the prediction endpoint.
    """
    amount: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Transaction amount in USD. Must be between $0.01 and $50,000.",
        examples=[129.99],
    )
    merchant_category: MerchantCategory = Field(
        ...,
        description="Category of the merchant where the transaction occurred.",
        examples=["electronics"],
    )
    transaction_hour: int = Field(
        ...,
        ge=0,
        le=23,
        description="Hour of day when transaction occurred (0-23).",
        examples=[14],
    )
    day_of_week: int = Field(
        default=3,
        ge=0,
        le=6,
        description="Day of week (0=Monday, 6=Sunday).",
        examples=[3],
    )
    location_distance_km: float = Field(
        default=0.0,
        ge=0,
        le=20000,
        description="Distance in km from cardholder's typical transaction location.",
        examples=[5.2],
    )
    is_international: bool = Field(
        default=False,
        description="Whether the transaction occurred in a different country.",
        examples=[False],
    )
    card_present: bool = Field(
        default=True,
        description="Whether the physical card was present at point of sale.",
        examples=[True],
    )
    velocity_last_1h: int = Field(
        default=1,
        ge=0,
        le=100,
        description="Number of transactions by this cardholder in the last hour.",
        examples=[1],
    )
    avg_amount_30d: float = Field(
        default=100.0,
        ge=0,
        le=50000,
        description="Cardholder's average transaction amount over the last 30 days.",
        examples=[85.50],
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float, info: ValidationInfo) -> float:
        """Ensure amount is strictly positive and rounded."""
        if v <= 0:
            raise ValueError("Transaction amount must be strictly greater than 0.")
        return round(v, 2)

    @field_validator("velocity_last_1h")
    @classmethod
    def validate_velocity(cls, v: int) -> int:
        """Velocity sanity check."""
        if v < 0:
            raise ValueError("Velocity cannot be negative.")
        if v > 100:
            raise ValueError("Velocity exceeds theoretical system maximum of 100 txn/hr.")
        return v

    def to_feature_dict(self) -> dict:
        """Convert the request to a dict suitable for feature engineering."""
        return {
            "amount": self.amount,
            "merchant_category": self.merchant_category.value,
            "transaction_hour": self.transaction_hour,
            "day_of_week": self.day_of_week,
            "location_distance_km": self.location_distance_km,
            "is_international": int(self.is_international),
            "card_present": int(self.card_present),
            "velocity_last_1h": self.velocity_last_1h,
            "avg_amount_30d": self.avg_amount_30d,
        }


class FeatureContribution(BaseModel):
    """A single feature's contribution to the fraud score."""
    feature: str
    contribution: float


class RuleResult(BaseModel):
    """Result from a single rule engine evaluation."""
    rule_id: str = Field(..., description="Rule identifier (e.g., R001)")
    rule_name: str = Field(..., description="Human-readable rule name")
    triggered: bool = Field(..., description="Whether this rule was triggered")
    action: str = Field(..., description="Rule action: BLOCK, ESCALATE, APPROVE, PASS")
    score_adjustment: float = Field(0.0, description="Score delta applied")
    reason: str = Field("", description="Explanation of why this rule fired")


class PredictionResponse(BaseModel):
    """Response schema for fraud prediction results."""
    transaction_id: str = Field(..., description="Unique identifier for this prediction.")
    fraud_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Final fraud probability after rule adjustments (0.0 to 1.0).",
    )
    ml_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Raw ML ensemble score before rule engine adjustments.",
    )
    risk_level: str = Field(
        ...,
        description="Risk category: Low, Medium, or High.",
    )
    decision: str = Field(
        "REVIEW",
        description="Final decision: APPROVED, BLOCKED, ESCALATED, or REVIEW.",
    )
    severity: str = Field(
        "low",
        description="SOC-style severity: critical, medium, or low.",
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="List of specific, human-readable fraud reasons.",
    )
    model_scores: dict[str, float] = Field(
        ...,
        description="Individual model scores contributing to the ensemble.",
    )
    # Rule Engine
    rules_triggered: list[str] = Field(
        default_factory=list,
        description="List of rule IDs that were triggered.",
    )
    rule_action: str = Field(
        "PASS",
        description="Aggregate rule action: BLOCK, ESCALATE, APPROVE, or PASS.",
    )
    rule_details: list[RuleResult] = Field(
        default_factory=list,
        description="Detailed results from each triggered rule.",
    )
    score_adjustment: float = Field(
        0.0,
        description="Total score adjustment from rule engine.",
    )
    # Explainability
    explanation: str = Field(
        ...,
        description="Human-readable explanation of why the transaction was flagged.",
    )
    top_risk_factors: list[FeatureContribution] = Field(
        ...,
        description="Top contributing features to the fraud score.",
    )
    is_llm_generated: bool = Field(
        default=False,
        description="Whether the explanation was generated by a Generative AI model.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of the prediction.",
    )


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""
    status: str = Field(..., description="Service status: 'healthy' or 'unhealthy'.")
    model_loaded: bool = Field(..., description="Whether ML models are loaded.")
    api_version: str = Field(..., description="Current API version.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: Optional[float] = Field(None, description="Server uptime in seconds.")


class TransactionRecord(BaseModel):
    """Schema for a stored transaction record returned by GET /transactions."""
    transaction_id: str
    amount: float
    merchant_category: str
    fraud_probability: float
    risk_level: str
    explanation: Optional[str] = None
    created_at: Optional[str] = None
    timestamp: Optional[str] = None


class StatsResponse(BaseModel):
    """Aggregate statistics for the dashboard."""
    total_transactions: int
    total_flagged: int
    fraud_rate: float
    avg_fraud_score: float
    risk_distribution: dict[str, int]
    recent_transactions: list[TransactionRecord]


class FeedbackRequest(BaseModel):
    """User feedback on a fraud prediction (learning loop)."""
    transaction_id: str = Field(..., description="ID of the transaction being reviewed.")
    action: str = Field(
        ...,
        description="User action: 'allow' or 'block'.",
    )
    reviewer: str = Field(
        default="analyst",
        description="Identifier of the human reviewer.",
    )
