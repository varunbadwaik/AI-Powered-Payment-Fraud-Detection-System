"""
Prediction service — 3-layer orchestration between API and ML models.

Pipeline:
    Layer 1: Advanced Feature Engineering (22 features)
    Layer 2: ML Ensemble Scoring (IF + LR + XGBoost)
    Layer 3: Rule Engine Post-Processing (8 deterministic rules)
    Layer 4: Advanced Reasoning Engine (contextual explanations)
    → Final Verdict + Severity + Audit Trail

This service layer keeps the API routes thin and the ML code decoupled.
"""

import uuid
from datetime import datetime, timezone

from models.inference import model_manager
from models.explainability import explain_prediction
from models.llm_explainer import generate_llm_explanation
from models.rule_engine import rule_engine, RuleEngineResult
from backend.database.models import store_transaction
from utils.logger import get_logger

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════════
#  Advanced Reasoning Engine
# ══════════════════════════════════════════════════════════════════
def _build_reasoning(transaction_data: dict, final_score: float, ml_score: float, rule_result) -> list[dict]:
    """
    Generate specific, human-readable fraud reasons based on
    transaction context — NOT generic ML jargon.

    Returns a list of reason dicts: [{reason, type, severity_boost}]
    """
    reasons = []
    amount = transaction_data.get("amount", 0)
    avg_30d = transaction_data.get("avg_amount_30d", 100)
    velocity = transaction_data.get("velocity_last_1h", 0)
    distance = transaction_data.get("location_distance_km", 0)
    hour = transaction_data.get("transaction_hour", 12)
    is_intl = transaction_data.get("is_international", 0)
    card_present = transaction_data.get("card_present", 1)

    # ── Amount Spike Analysis ─────────────────────────────────────
    if avg_30d > 0:
        ratio = amount / avg_30d
        if ratio > 5:
            reasons.append({
                "reason": f"Transaction amount ${amount:,.0f} is {ratio:.1f}x higher than user baseline (${avg_30d:,.0f})",
                "type": "amount_spike",
                "severity_boost": 0.3,
            })
        elif ratio > 3:
            reasons.append({
                "reason": f"Amount ${amount:,.0f} is {ratio:.1f}x above 30-day average (${avg_30d:,.0f})",
                "type": "amount_spike",
                "severity_boost": 0.15,
            })

    # ── Location Anomaly ──────────────────────────────────────────
    if distance > 500:
        reasons.append({
            "reason": f"Location anomaly: transaction {distance:,.0f}km from home — possible new country",
            "type": "location_anomaly",
            "severity_boost": 0.25,
        })
    elif distance > 100:
        reasons.append({
            "reason": f"Location deviation: {distance:,.0f}km from usual transaction zone",
            "type": "location_anomaly",
            "severity_boost": 0.1,
        })

    # ── Velocity Surge ────────────────────────────────────────────
    if velocity >= 8:
        reasons.append({
            "reason": f"Velocity spike: {velocity} transactions in last hour — possible card testing",
            "type": "velocity_surge",
            "severity_boost": 0.3,
        })
    elif velocity >= 4:
        reasons.append({
            "reason": f"Elevated velocity: {velocity} transactions in last hour (normal: 1-2)",
            "type": "velocity_surge",
            "severity_boost": 0.1,
        })

    # ── Time-Based Behavioral Anomaly ─────────────────────────────
    if hour >= 0 and hour <= 5:
        reasons.append({
            "reason": f"Unusual timing: transaction at {hour}:00 — user typically transacts 9AM-6PM",
            "type": "time_anomaly",
            "severity_boost": 0.15,
        })

    # ── International + Card-Not-Present Combo ────────────────────
    if is_intl and not card_present:
        reasons.append({
            "reason": "High-risk combination: international transaction without physical card present",
            "type": "intl_cnp_combo",
            "severity_boost": 0.2,
        })

    # ── Rule Engine Triggers ──────────────────────────────────────
    for rule_id in (rule_result.triggered_rules or []):
        if rule_id not in [r.get("type") for r in reasons]:
            reasons.append({
                "reason": f"Rule engine flag: {rule_id} triggered",
                "type": "rule_engine",
                "severity_boost": 0.05,
            })

    # ── Fallback for low-risk ─────────────────────────────────────
    if not reasons:
        reasons.append({
            "reason": "Transaction patterns consistent with user baseline — no anomalies detected",
            "type": "clean",
            "severity_boost": 0.0,
        })

    return reasons


def _classify_severity(final_score: float, decision: str, reasons: list[dict]) -> str:
    """Map to SOC-style severity: critical / medium / low."""
    if decision == "BLOCKED" or final_score >= 0.85:
        return "critical"
    elif decision in ("ESCALATED", "REVIEW") or final_score >= 0.45:
        return "medium"
    return "low"


async def predict_fraud(transaction_data: dict) -> dict:
    """
    Full 4-layer fraud prediction pipeline for a single transaction.

    Args:
        transaction_data: Dict of validated transaction features.

    Returns:
        Complete prediction response dict ready for API serialization.
    """
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    logger.info(
        f"Processing prediction for {transaction_id} | "
        f"amount=${transaction_data.get('amount', 0):.2f}"
    )

    # ══════════════════════════════════════════════════════════════════
    #  Layer 1 + 2: Feature Engineering → ML Ensemble
    # ══════════════════════════════════════════════════════════════════
    try:
        prediction = model_manager.predict(transaction_data)
    except RuntimeError as e:
        logger.error(f"Model inference failed: {e}")
        raise

    ml_score = prediction["fraud_probability"]
    ml_risk = prediction["risk_level"]

    # ══════════════════════════════════════════════════════════════════
    #  Layer 3: Rule-Based Post-Processing
    # ══════════════════════════════════════════════════════════════════
    rule_result: RuleEngineResult = rule_engine.evaluate(
        transaction=transaction_data,
        ml_score=ml_score,
    )

    # Apply rule adjustments to ML score
    final_score = ml_score + rule_result.total_score_adjustment
    final_score = max(0.0, min(1.0, final_score))

    # Determine final decision
    if rule_result.final_action == "BLOCK":
        final_risk = "High"
        decision = "BLOCKED"
        final_score = max(final_score, 0.95)  # Force high score
    elif rule_result.final_action == "APPROVE":
        final_risk = "Low"
        decision = "APPROVED"
    elif rule_result.final_action == "ESCALATE":
        final_risk = model_manager._classify_risk(final_score)
        decision = "ESCALATED"
    else:
        final_risk = ml_risk
        decision = "APPROVED" if ml_risk == "Low" else "REVIEW"

    # ══════════════════════════════════════════════════════════════════
    #  Layer 4: Advanced Reasoning Engine
    # ══════════════════════════════════════════════════════════════════
    reasons = _build_reasoning(transaction_data, final_score, ml_score, rule_result)
    severity = _classify_severity(final_score, decision, reasons)

    # ══════════════════════════════════════════════════════════════════
    #  Explainability (SHAP-style + LLM)
    # ══════════════════════════════════════════════════════════════════
    explanation_result = explain_prediction(
        feature_values=prediction["feature_values"],
        top_n=3,
    )

    # Try to enhance with LLM Generative AI
    llm_explanation = await generate_llm_explanation(
        transaction_data=transaction_data,
        risk_score=final_score,
        top_factors=[(f["feature"], f["contribution"]) for f in explanation_result["top_factors"]],
        decision=decision,
    )

    if llm_explanation:
        explanation_result["explanation_text"] = llm_explanation
        explanation_result["is_llm_generated"] = True
    else:
        # Use the best contextual reason as the primary explanation
        explanation_result["explanation_text"] = reasons[0]["reason"]
        explanation_result["is_llm_generated"] = False

    # ══════════════════════════════════════════════════════════════════
    #  Build Response
    # ══════════════════════════════════════════════════════════════════
    response = {
        "transaction_id": transaction_id,
        # ML Scores
        "fraud_probability": final_score,
        "ml_score": ml_score,
        "risk_level": final_risk,
        "decision": decision,
        "model_scores": prediction["model_scores"],
        # Severity & Reasoning
        "severity": severity,
        "reasons": [r["reason"] for r in reasons],
        # Rule Engine
        "rules_triggered": rule_result.triggered_rules,
        "rule_action": rule_result.final_action,
        "rule_details": [
            v.to_dict() for v in rule_result.verdicts if v.triggered
        ],
        "score_adjustment": rule_result.total_score_adjustment,
        # Explainability
        "explanation": explanation_result["explanation_text"],
        "top_risk_factors": explanation_result["top_factors"],
        "is_llm_generated": explanation_result.get("is_llm_generated", False),
        "timestamp": datetime.now(timezone.utc),
    }

    # ══════════════════════════════════════════════════════════════════
    #  Logging by severity
    # ══════════════════════════════════════════════════════════════════
    rules_str = ", ".join(rule_result.triggered_rules) if rule_result.triggered_rules else "none"

    if decision == "BLOCKED":
        logger.warning(
            f"🚫 BLOCKED [{severity.upper()}]: {transaction_id} | "
            f"ml={ml_score:.4f} final={final_score:.4f} | "
            f"rules={rules_str}"
        )
    elif decision == "ESCALATED":
        logger.warning(
            f"⚠️ ESCALATED [{severity.upper()}]: {transaction_id} | "
            f"ml={ml_score:.4f} final={final_score:.4f} | "
            f"rules={rules_str}"
        )
    else:
        logger.info(
            f"✅ {decision} [{severity.upper()}]: {transaction_id} | "
            f"ml={ml_score:.4f} final={final_score:.4f} | "
            f"rules={rules_str}"
        )

    # ══════════════════════════════════════════════════════════════════
    #  Persist to Database (non-blocking)
    # ══════════════════════════════════════════════════════════════════
    try:
        await store_transaction(
            transaction_id=transaction_id,
            transaction_data=transaction_data,
            prediction_result={
                **prediction,
                "fraud_probability": final_score,
                "risk_level": final_risk,
            },
            explanation=explanation_result["explanation_text"],
        )
    except Exception as e:
        # Don't fail the prediction if DB write fails
        logger.error(f"Failed to store transaction {transaction_id}: {e}")

    return response
