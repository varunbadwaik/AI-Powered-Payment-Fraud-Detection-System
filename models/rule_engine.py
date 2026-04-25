"""
Deterministic Rule-Based Fraud Engine for the Fraud Detection System.

Runs AFTER ML scoring to apply hard business rules that override
or adjust the ML ensemble output. This hybrid approach combines
statistical learning with domain expertise.

Rule Categories:
    - HARD BLOCK:  Instant reject, no override (R001-R003)
    - ESCALATION:  Boost ML score toward High risk (R004-R007)
    - AUTO APPROVE: Fast-track clearly safe transactions (R008)

Each rule produces a RuleVerdict with:
    - triggered: bool
    - action: BLOCK / ESCALATE / APPROVE / PASS
    - score_adjustment: float delta to apply to ML score
    - reason: human-readable explanation
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from utils.logger import get_logger

logger = get_logger(__name__)

# Default config path
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "fraud_thresholds.yaml"


@dataclass
class RuleVerdict:
    """Result of a single rule evaluation."""
    rule_id: str
    rule_name: str
    triggered: bool
    action: Literal["BLOCK", "ESCALATE", "APPROVE", "PASS"]
    score_adjustment: float = 0.0
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "triggered": self.triggered,
            "action": self.action,
            "score_adjustment": self.score_adjustment,
            "reason": self.reason,
        }


@dataclass
class RuleEngineResult:
    """Aggregate result from all rules."""
    verdicts: list[RuleVerdict] = field(default_factory=list)
    final_action: Literal["BLOCK", "ESCALATE", "APPROVE", "PASS"] = "PASS"
    total_score_adjustment: float = 0.0
    triggered_rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "final_action": self.final_action,
            "total_score_adjustment": self.total_score_adjustment,
            "triggered_rules": self.triggered_rules,
            "verdicts": [v.to_dict() for v in self.verdicts if v.triggered],
        }


class FraudRuleEngine:
    """
    Deterministic rule engine that evaluates transactions
    against a set of configurable fraud rules.

    Rules are loaded from fraud_thresholds.yaml and can be
    tuned by fraud analysts without code changes.
    """

    def __init__(self, config_path: str | Path | None = None):
        self._config = self._load_config(config_path or _CONFIG_PATH)
        self._enabled = self._config.get("rule_engine", {}).get("enabled", True)
        self._hard_block = self._config.get("rule_engine", {}).get("hard_block", {})
        self._escalation = self._config.get("rule_engine", {}).get("escalation", {})
        self._auto_approve = self._config.get("rule_engine", {}).get("auto_approve", {})

    @staticmethod
    def _load_config(path: str | Path) -> dict:
        """Load rule configuration from YAML."""
        path = Path(path)
        if not path.exists():
            logger.warning(f"Rule config not found at {path}, using defaults")
            return {}
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    def evaluate(
        self,
        transaction: dict,
        ml_score: float,
    ) -> RuleEngineResult:
        """
        Evaluate all rules against a transaction.

        Args:
            transaction: Dict with raw + engineered features.
            ml_score: ML ensemble fraud probability (0-1).

        Returns:
            RuleEngineResult with all verdicts and final action.
        """
        if not self._enabled:
            return RuleEngineResult(final_action="PASS")

        verdicts = [
            self._r001_velocity_circuit_breaker(transaction),
            self._r002_amount_ceiling(transaction),
            self._r003_geographic_impossibility(transaction),
            self._r004_night_intl_cnp(transaction),
            self._r005_amount_spike(transaction),
            self._r006_rapid_micro_txns(transaction),
            self._r007_round_amount_intl(transaction),
            self._r008_auto_approve(transaction, ml_score),
        ]

        return self._aggregate(verdicts)

    def _aggregate(self, verdicts: list[RuleVerdict]) -> RuleEngineResult:
        """Combine individual rule verdicts into a final decision."""
        result = RuleEngineResult(verdicts=verdicts)

        # Priority: BLOCK > ESCALATE > APPROVE > PASS
        for v in verdicts:
            if v.triggered:
                result.triggered_rules.append(v.rule_id)
                result.total_score_adjustment += v.score_adjustment

                if v.action == "BLOCK":
                    result.final_action = "BLOCK"
                    # Short-circuit: block overrides everything
                    return result

        # Check for escalations
        has_escalation = any(
            v.triggered and v.action == "ESCALATE" for v in verdicts
        )
        has_approve = any(
            v.triggered and v.action == "APPROVE" for v in verdicts
        )

        if has_escalation:
            result.final_action = "ESCALATE"
        elif has_approve and not has_escalation:
            result.final_action = "APPROVE"
        else:
            result.final_action = "PASS"

        return result

    # ==================================================================
    #  Rule Implementations
    # ==================================================================

    def _r001_velocity_circuit_breaker(self, txn: dict) -> RuleVerdict:
        """R001: Hard block when transaction velocity exceeds safety threshold."""
        threshold = self._hard_block.get("max_velocity_1h", 15)
        velocity = txn.get("velocity_last_1h", 0)

        triggered = velocity > threshold
        return RuleVerdict(
            rule_id="R001",
            rule_name="Velocity Circuit Breaker",
            triggered=triggered,
            action="BLOCK" if triggered else "PASS",
            score_adjustment=0.5 if triggered else 0.0,
            reason=(
                f"Transaction velocity ({velocity} txns/hr) exceeds "
                f"safety threshold ({threshold}). Possible card compromise."
                if triggered else ""
            ),
        )

    def _r002_amount_ceiling(self, txn: dict) -> RuleVerdict:
        """R002: Hard block for amounts exceeding absolute ceiling."""
        ceiling = self._hard_block.get("max_amount", 25000)
        amount = txn.get("amount", 0)

        triggered = amount > ceiling
        return RuleVerdict(
            rule_id="R002",
            rule_name="Amount Ceiling Breach",
            triggered=triggered,
            action="BLOCK" if triggered else "PASS",
            score_adjustment=0.5 if triggered else 0.0,
            reason=(
                f"Transaction amount (${amount:,.2f}) exceeds "
                f"maximum allowed (${ceiling:,.2f})."
                if triggered else ""
            ),
        )

    def _r003_geographic_impossibility(self, txn: dict) -> RuleVerdict:
        """R003: Hard block for geographically impossible transactions."""
        max_dist = self._hard_block.get("max_distance_km", 10000)
        distance = txn.get("location_distance_km", 0)

        triggered = distance > max_dist
        return RuleVerdict(
            rule_id="R003",
            rule_name="Geographic Impossibility",
            triggered=triggered,
            action="BLOCK" if triggered else "PASS",
            score_adjustment=0.5 if triggered else 0.0,
            reason=(
                f"Transaction location ({distance:,.0f} km away) exceeds "
                f"maximum plausible distance ({max_dist:,.0f} km)."
                if triggered else ""
            ),
        )

    def _r004_night_intl_cnp(self, txn: dict) -> RuleVerdict:
        """R004: Escalate when night + international + card-not-present all true."""
        hour = txn.get("transaction_hour", 12)
        is_night = hour <= 5 or hour >= 22
        is_intl = bool(txn.get("is_international", 0))
        is_cnp = not bool(txn.get("card_present", 1))

        triggered = is_night and is_intl and is_cnp
        boost = self._escalation.get("night_intl_cnp_boost", 0.30)

        return RuleVerdict(
            rule_id="R004",
            rule_name="Night + International + CNP",
            triggered=triggered,
            action="ESCALATE" if triggered else "PASS",
            score_adjustment=boost if triggered else 0.0,
            reason=(
                f"High-risk combination: late night (hour {hour}), "
                f"international, card-not-present. Score boosted +{boost:.0%}."
                if triggered else ""
            ),
        )

    def _r005_amount_spike(self, txn: dict) -> RuleVerdict:
        """R005: Escalate when amount is many multiples of user's average."""
        multiplier = self._escalation.get("amount_spike_multiplier", 10)
        boost = self._escalation.get("amount_spike_boost", 0.25)
        amount = txn.get("amount", 0)
        avg = txn.get("avg_amount_30d", 1)

        ratio = amount / avg if avg > 0 else 0
        triggered = ratio > multiplier

        return RuleVerdict(
            rule_id="R005",
            rule_name="Amount Spike Detection",
            triggered=triggered,
            action="ESCALATE" if triggered else "PASS",
            score_adjustment=boost if triggered else 0.0,
            reason=(
                f"Amount (${amount:,.2f}) is {ratio:.1f}x the 30-day average "
                f"(${avg:,.2f}). Threshold: {multiplier}x. Score boosted +{boost:.0%}."
                if triggered else ""
            ),
        )

    def _r006_rapid_micro_txns(self, txn: dict) -> RuleVerdict:
        """R006: Escalate rapid micro-transactions (card testing pattern)."""
        vel_min = self._escalation.get("micro_txn_velocity_min", 8)
        amt_max = self._escalation.get("micro_txn_amount_max", 5)
        boost = self._escalation.get("micro_txn_boost", 0.20)

        velocity = txn.get("velocity_last_1h", 0)
        amount = txn.get("amount", 0)

        triggered = velocity >= vel_min and amount <= amt_max

        return RuleVerdict(
            rule_id="R006",
            rule_name="Card Testing Detection",
            triggered=triggered,
            action="ESCALATE" if triggered else "PASS",
            score_adjustment=boost if triggered else 0.0,
            reason=(
                f"Card testing pattern: {velocity} micro-transactions "
                f"(≤${amt_max}) in the last hour. Score boosted +{boost:.0%}."
                if triggered else ""
            ),
        )

    def _r007_round_amount_intl(self, txn: dict) -> RuleVerdict:
        """R007: Escalate round-amount international transactions."""
        boost = self._escalation.get("round_intl_boost", 0.15)
        amount = txn.get("amount", 0)
        is_intl = bool(txn.get("is_international", 0))
        is_round = amount >= 100 and amount % 100 == 0

        triggered = is_round and is_intl

        return RuleVerdict(
            rule_id="R007",
            rule_name="Round Amount + International",
            triggered=triggered,
            action="ESCALATE" if triggered else "PASS",
            score_adjustment=boost if triggered else 0.0,
            reason=(
                f"Round amount (${amount:,.0f}) on international transaction. "
                f"Score boosted +{boost:.0%}."
                if triggered else ""
            ),
        )

    def _r008_auto_approve(self, txn: dict, ml_score: float) -> RuleVerdict:
        """R008: Auto-approve small, low-score transactions."""
        max_amount = self._auto_approve.get("max_amount", 50)
        max_score = self._auto_approve.get("max_score", 0.15)
        amount = txn.get("amount", 0)

        triggered = amount <= max_amount and ml_score <= max_score

        return RuleVerdict(
            rule_id="R008",
            rule_name="Low-Risk Auto-Approve",
            triggered=triggered,
            action="APPROVE" if triggered else "PASS",
            score_adjustment=0.0,
            reason=(
                f"Small transaction (${amount:,.2f}) with low ML score "
                f"({ml_score:.1%}). Auto-approved."
                if triggered else ""
            ),
        )


# Module-level singleton
rule_engine = FraudRuleEngine()
