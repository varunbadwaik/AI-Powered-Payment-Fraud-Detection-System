"""
Professional banking-grade risk indicator components.

Provides:
    - Animated risk badges with glow effects (Red/Yellow/Green)
    - Real-time pipeline visualizer: Transaction → Risk → Alert → Action
    - Fraud alert popup with severity-based styling
    - Premium KPI cards with trend indicators
    - Model score breakdown panels
"""

import streamlit as st


# ── Badge colour map ──────────────────────────────────────────────────
_RISK_THEME = {
    "Low": {
        "bg": "linear-gradient(135deg, #064e3b 0%, #065f46 100%)",
        "border": "#10b981",
        "text": "#34d399",
        "glow": "rgba(16,185,129,0.25)",
        "icon": "✓",
        "label": "CLEARED",
        "action": "Auto-Approved",
        "action_icon": "✅",
    },
    "Medium": {
        "bg": "linear-gradient(135deg, #78350f 0%, #92400e 100%)",
        "border": "#f59e0b",
        "text": "#fbbf24",
        "glow": "rgba(245,158,11,0.25)",
        "icon": "⚠",
        "label": "REVIEW",
        "action": "Escalate to Analyst",
        "action_icon": "👁️",
    },
    "High": {
        "bg": "linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)",
        "border": "#ef4444",
        "text": "#f87171",
        "glow": "rgba(239,68,68,0.35)",
        "icon": "✕",
        "label": "BLOCKED",
        "action": "Hold & Investigate",
        "action_icon": "🚨",
    },
}


def render_risk_badge(risk_level: str, fraud_probability: float) -> None:
    """Display a large animated risk badge with glow effect."""
    t = _RISK_THEME.get(risk_level, _RISK_THEME["Low"])
    pct = fraud_probability * 100

    st.markdown(f"""<div style="background:{t['bg']};border:2px solid {t['border']};border-radius:20px;padding:28px 24px;text-align:center;margin-bottom:20px;box-shadow:0 0 20px {t['glow']};position:relative;overflow:hidden;">
<div style="position:absolute;top:0;right:0;width:80px;height:80px;background:{t['border']};opacity:0.06;border-radius:0 20px 0 80px;"></div>
<div style="display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:50%;background:rgba(0,0,0,0.25);border:2px solid {t['border']};font-size:28px;margin-bottom:12px;">{t['icon']}</div>
<div style="font-size:13px;font-weight:600;color:{t['text']};letter-spacing:3px;">{t['label']}</div>
<div style="font-size:26px;font-weight:800;color:#f1f5f9;letter-spacing:1px;">{risk_level.upper()} RISK</div>
<div style="font-size:48px;font-weight:800;color:{t['text']};margin:8px 0 4px;font-variant-numeric:tabular-nums;">{pct:.1f}<span style="font-size:24px;opacity:0.7;">%</span></div>
<div style="font-size:12px;color:#94a3b8;letter-spacing:1px;">FRAUD PROBABILITY</div>
</div>""", unsafe_allow_html=True)


def render_fraud_gauge(fraud_probability: float) -> None:
    """Render a segmented progress gauge with threshold markers."""
    pct = fraud_probability * 100
    if fraud_probability < 0.3:
        fill = "linear-gradient(90deg, #10b981, #34d399)"
    elif fraud_probability < 0.7:
        fill = "linear-gradient(90deg, #10b981, #f59e0b)"
    else:
        fill = "linear-gradient(90deg, #10b981, #f59e0b, #ef4444)"

    st.markdown(f"""<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
<div style="display:flex;justify-content:space-between;font-size:11px;font-weight:600;color:#64748b;margin-bottom:8px;letter-spacing:1px;">
<span style="color:#34d399">● SAFE</span>
<span style="color:#fbbf24">● SUSPICIOUS</span>
<span style="color:#f87171">● FRAUDULENT</span>
</div>
<div style="background:#1e293b;border-radius:10px;height:14px;overflow:hidden;position:relative;">
<div style="position:absolute;left:30%;top:0;bottom:0;width:2px;background:rgba(255,255,255,0.15);z-index:2;"></div>
<div style="position:absolute;left:70%;top:0;bottom:0;width:2px;background:rgba(255,255,255,0.15);z-index:2;"></div>
<div style="width:{pct}%;height:100%;background:{fill};border-radius:10px;"></div>
</div></div>""", unsafe_allow_html=True)


def render_pipeline_status(risk_level: str, fraud_probability: float) -> None:
    """Render the real-time pipeline: Transaction → Risk Engine → Alert → Action."""
    t = _RISK_THEME.get(risk_level, _RISK_THEME["Low"])
    score_text = f"{fraud_probability:.1%}"

    # Use Streamlit columns for the pipeline stages instead of complex HTML
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid #334155;border-radius:14px;padding:16px 20px;margin-bottom:20px;">
<div style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:2px;margin-bottom:16px;">REAL-TIME PIPELINE</div>
<div style="display:flex;align-items:center;justify-content:space-between;">
<div style="text-align:center;flex:1;">
<div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:rgba(0,0,0,0.3);border:1.5px solid #6366f1;font-size:20px;margin-bottom:8px;">📨</div>
<div style="font-size:11px;font-weight:700;color:#e2e8f0;">Transaction</div>
<div style="font-size:10px;color:#6366f1;font-weight:600;">Received</div>
</div>
<div style="color:#475569;font-size:18px;">→</div>
<div style="text-align:center;flex:1;">
<div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:rgba(0,0,0,0.3);border:1.5px solid #8b5cf6;font-size:20px;margin-bottom:8px;">🧠</div>
<div style="font-size:11px;font-weight:700;color:#e2e8f0;">Risk Engine</div>
<div style="font-size:10px;color:#8b5cf6;font-weight:600;">Score: {score_text}</div>
</div>
<div style="color:#475569;font-size:18px;">→</div>
<div style="text-align:center;flex:1;">
<div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:rgba(0,0,0,0.3);border:1.5px solid {t['border']};font-size:20px;margin-bottom:8px;">{t['icon']}</div>
<div style="font-size:11px;font-weight:700;color:#e2e8f0;">Alert Level</div>
<div style="font-size:10px;color:{t['border']};font-weight:600;">{risk_level.upper()}</div>
</div>
<div style="color:#475569;font-size:18px;">→</div>
<div style="text-align:center;flex:1;">
<div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:rgba(0,0,0,0.3);border:1.5px solid {t['border']};font-size:20px;margin-bottom:8px;">{t['action_icon']}</div>
<div style="font-size:11px;font-weight:700;color:#e2e8f0;">Action</div>
<div style="font-size:10px;color:{t['border']};font-weight:600;">{t['action']}</div>
</div>
</div></div>""", unsafe_allow_html=True)


def render_fraud_alert_popup(risk_level: str, fraud_probability: float, transaction_id: str) -> None:
    """Display a fraud alert popup for Medium/High risk transactions."""
    t = _RISK_THEME.get(risk_level, _RISK_THEME["Low"])

    if risk_level == "Low":
        st.markdown(f"""<div style="background:linear-gradient(135deg,#064e3b,#065f46);border-left:4px solid #10b981;border-radius:0 12px 12px 0;padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:12px;">
<span style="font-size:24px;">✅</span>
<div><div style="font-size:14px;font-weight:700;color:#34d399;">Transaction Approved</div>
<div style="font-size:12px;color:#6ee7b7;">{transaction_id} — No suspicious indicators detected</div></div>
</div>""", unsafe_allow_html=True)
        return

    severity = "CRITICAL ALERT" if risk_level == "High" else "CAUTION ALERT"
    border_w = "3px" if risk_level == "High" else "2px"

    st.markdown(f"""<div style="background:{t['bg']};border:{border_w} solid {t['border']};border-radius:16px;padding:24px;margin-bottom:20px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;right:0;width:100px;height:100px;background:{t['border']};opacity:0.05;border-radius:0 16px 0 100px;"></div>
<div style="display:flex;align-items:flex-start;gap:16px;position:relative;">
<div style="flex-shrink:0;width:48px;height:48px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:rgba(0,0,0,0.3);border:2px solid {t['border']};font-size:24px;">🚨</div>
<div style="flex:1;">
<div style="font-size:11px;font-weight:800;color:{t['text']};letter-spacing:2px;margin-bottom:4px;">{severity}</div>
<div style="font-size:18px;font-weight:700;color:#f1f5f9;margin-bottom:8px;">Fraud Detected — {fraud_probability:.1%} Confidence</div>
<div style="font-size:13px;color:#cbd5e1;line-height:1.5;">Transaction <span style="background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px;font-size:12px;color:{t['text']};font-family:monospace;">{transaction_id}</span> has been flagged.<br><strong style="color:{t['text']}">Recommended action:</strong> {t['action']}</div>
</div></div></div>""", unsafe_allow_html=True)


def render_explanation_card(explanation: str, top_factors: list[dict], is_llm: bool = False) -> None:
    """Display the AI explanation with top contributing factors as styled bars."""
    badge = "✨ AI-Generated (LLM)" if is_llm else "🧠 Deterministic Template"
    badge_color = "#8b5cf6" if is_llm else "#6366f1"
    
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid #334155;border-radius:14px;padding:20px;margin:16px 0;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
<div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);font-size:16px;">💬</div>
<span style="font-size:14px;font-weight:700;color:#e2e8f0;">Explanation Report</span>
<span style="margin-left:auto;font-size:10px;font-weight:700;color:{badge_color};letter-spacing:1px;background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:12px;border:1px solid {badge_color}33;">{badge}</span>
</div>
<div style="font-size:13px;color:#94a3b8;line-height:1.6;padding:12px 16px;background:rgba(0,0,0,0.2);border-radius:8px;border-left:3px solid {badge_color};">{explanation}</div>
</div>""", unsafe_allow_html=True)

    if top_factors:
        max_contrib = max(abs(f.get("contribution", 0)) for f in top_factors) or 1
        rows = ""
        for factor in top_factors:
            c = factor.get("contribution", 0)
            feat = factor.get("feature", "Unknown")
            bar_w = min(abs(c) / max_contrib * 100, 100)
            bar_col = "#ef4444" if c > 0 else "#10b981"
            d = "▲ Risk" if c > 0 else "▼ Safe"
            dc = "#f87171" if c > 0 else "#34d399"
            rows += f"""<div style="display:flex;align-items:center;padding:10px 0;border-bottom:1px solid #1e293b;">
<div style="flex:1;font-size:13px;color:#e2e8f0;font-weight:500;">{feat}</div>
<div style="width:120px;margin:0 12px;"><div style="background:#0f172a;border-radius:4px;height:8px;overflow:hidden;"><div style="width:{bar_w}%;height:100%;background:{bar_col};border-radius:4px;"></div></div></div>
<div style="width:80px;text-align:right;font-size:11px;font-weight:700;color:{dc};">{d}</div>
</div>"""

        st.markdown(f"""<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px 20px;margin-bottom:16px;">
<div style="font-size:12px;font-weight:700;color:#64748b;letter-spacing:1.5px;margin-bottom:8px;">TOP RISK FACTORS</div>
{rows}</div>""", unsafe_allow_html=True)


def render_model_scores(model_scores: dict) -> None:
    """Display individual model scores as styled cards."""
    icons = {"isolation_forest_score": "🌲", "logistic_regression_score": "📈"}
    names = {"isolation_forest_score": "Isolation Forest", "logistic_regression_score": "Logistic Regression"}

    cards = ""
    for model, score in model_scores.items():
        name = names.get(model, model.replace("_", " ").title())
        icon = icons.get(model, "🔬")
        pct = score * 100
        sc = "#10b981" if score < 0.3 else "#f59e0b" if score < 0.7 else "#ef4444"
        cards += f"""<div style="flex:1;background:#0f172a;border:1px solid #334155;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:20px;margin-bottom:6px;">{icon}</div>
<div style="font-size:11px;color:#64748b;font-weight:600;letter-spacing:0.5px;">{name}</div>
<div style="font-size:28px;font-weight:800;color:{sc};margin-top:4px;font-variant-numeric:tabular-nums;">{pct:.1f}%</div>
</div>"""

    st.markdown(f'<div style="display:flex;gap:12px;margin-bottom:16px;">{cards}</div>', unsafe_allow_html=True)


def render_kpi_cards(stats: dict) -> None:
    """Render premium KPI cards with glowing accents."""
    total = stats.get("total_transactions", 0)
    flagged = stats.get("total_flagged", 0)
    fraud_rate = stats.get("fraud_rate", 0)
    avg_score = stats.get("avg_fraud_score", 0)

    kpis = [
        ("📊", "Total Transactions", f"{total:,}", "#6366f1", "All time processed"),
        ("🚩", "Flagged Alerts", f"{flagged:,}", "#ef4444" if flagged > 0 else "#10b981", "Medium + High risk"),
        ("📈", "Flag Rate", f"{fraud_rate:.1%}", "#f59e0b" if fraud_rate > 0.05 else "#10b981", "Flagged / Total"),
        ("🎯", "Avg Risk Score", f"{avg_score:.4f}", "#8b5cf6", "Ensemble output"),
    ]

    cards = ""
    for icon, label, value, color, sub in kpis:
        cards += f"""<div style="flex:1;background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #334155;border-radius:16px;padding:20px;position:relative;overflow:hidden;min-width:0;">
<div style="position:absolute;top:-10px;right:-10px;width:60px;height:60px;border-radius:50%;background:{color};opacity:0.06;"></div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
<span style="font-size:18px;">{icon}</span>
<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1px;">{label.upper()}</span>
</div>
<div style="font-size:28px;font-weight:800;color:{color};font-variant-numeric:tabular-nums;margin-bottom:4px;">{value}</div>
<div style="font-size:11px;color:#475569;font-weight:500;">{sub}</div>
</div>"""

    st.markdown(f'<div style="display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap;">{cards}</div>', unsafe_allow_html=True)


def render_rule_engine_verdict(decision: str, rules_triggered: list[str], rule_details: list[dict], score_adjustment: float) -> None:
    """Render the deterministic rule engine verdict and triggers."""
    if not rules_triggered and score_adjustment == 0:
        return  # No rules fired, purely ML decision

    if decision == "BLOCKED":
        bg, border, text, icon = "#7f1d1d", "#ef4444", "#f87171", "🛑"
    elif decision == "ESCALATED":
        bg, border, text, icon = "#78350f", "#f59e0b", "#fbbf24", "⚠️"
    elif decision == "APPROVED":
        bg, border, text, icon = "#064e3b", "#10b981", "#34d399", "✅"
    else:
        bg, border, text, icon = "#1e293b", "#64748b", "#cbd5e1", "⚙️"

    st.markdown(f"""<div style="background:{bg};border:1px solid {border};border-radius:14px;padding:20px;margin-bottom:20px;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
<div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:rgba(0,0,0,0.3);border:1px solid {border};font-size:16px;">{icon}</div>
<span style="font-size:14px;font-weight:700;color:{text};">Rule Engine Post-Processing</span>
<span style="margin-left:auto;font-size:12px;font-weight:700;color:{text};background:rgba(0,0,0,0.3);padding:4px 10px;border-radius:12px;">Adjustment: {score_adjustment:+.2f}</span>
</div>
""", unsafe_allow_html=True)

    rows = ""
    for rule in rule_details:
        r_action = rule.get("action", "")
        r_color = "#ef4444" if r_action == "BLOCK" else "#f59e0b" if r_action == "ESCALATE" else "#10b981"
        rows += f"""<div style="background:rgba(0,0,0,0.2);border-left:3px solid {r_color};border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:8px;">
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
<span style="font-size:12px;font-weight:700;color:#e2e8f0;letter-spacing:1px;">{rule.get('rule_id')} — {rule.get('rule_name')}</span>
<span style="font-size:10px;font-weight:800;color:{r_color};">{r_action}</span>
</div>
<div style="font-size:12px;color:#94a3b8;">{rule.get('reason')}</div>
</div>"""



def render_model_performance_metrics(metrics: dict) -> None:
    """Render a compact dashboard section for model performance metrics."""
    # Try to grab XGBoost metrics first, fallback to LR, then IF.
    best_model = metrics.get("xgboost") or metrics.get("logistic_regression") or metrics.get("isolation_forest") or {}
    
    accuracy = best_model.get("accuracy", 0.0)
    precision = best_model.get("precision_fraud", 0.0)
    recall = best_model.get("recall_fraud", 0.0)
    
    # Fraud Detection Rate (Recall represents what % of true fraud we detected)
    detection_rate = recall
    
    cm = best_model.get("confusion_matrix", [[0, 0], [0, 0]])
    true_neg = cm[0][0] if cm else 0
    false_pos = cm[0][1] if cm else 0
    false_neg = cm[1][0] if cm else 0
    true_pos = cm[1][1] if cm else 0

    st.markdown(
        '<div style="font-size:11px; font-weight:700; color:#64748b; letter-spacing:1.5px; margin-bottom:12px;">🧪 MODEL PERFORMANCE (LATEST TRAINING)</div>',
        unsafe_allow_html=True,
    )
    
    kpis = [
        ("🎯", "Accuracy", f"{accuracy:.1%}", "#34d399"),
        ("⚡", "Detection Rate", f"{detection_rate:.1%}", "#6366f1"),
        ("🛡️", "Precision", f"{precision:.1%}", "#8b5cf6"),
        ("🔍", "Recall", f"{recall:.1%}", "#f59e0b"),
    ]

    cards = ""
    for icon, label, value, color in kpis:
        cards += f"""<div style="flex:1;background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #334155;border-radius:12px;padding:16px;position:relative;overflow:hidden;min-width:0;text-align:center;">
<div style="font-size:24px;margin-bottom:8px;">{icon}</div>
<div style="font-size:10px;font-weight:700;color:#64748b;letter-spacing:1px;margin-bottom:4px;">{label.upper()}</div>
<div style="font-size:22px;font-weight:800;color:{color};font-variant-numeric:tabular-nums;">{value}</div>
</div>"""

    st.markdown(f'<div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;">{cards}</div>', unsafe_allow_html=True)
    
    # Confusion Matrix Visual
    st.markdown(f"""
    <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:16px;">
        <div style="font-size:10px; font-weight:700; color:#64748b; margin-bottom:12px; text-align:center;">CONFUSION MATRIX</div>
        <div style="display:flex; gap:16px; justify-content:center;">
            <div style="text-align:center; padding:12px; background:rgba(16,185,129,0.1); border:1px solid #10b981; border-radius:8px; width:120px;">
                <div style="font-size:18px; font-weight:800; color:#34d399;">{true_neg}</div>
                <div style="font-size:10px; color:#94a3b8;">True Normal</div>
            </div>
            <div style="text-align:center; padding:12px; background:rgba(239,68,68,0.1); border:1px solid #ef4444; border-radius:8px; width:120px;">
                <div style="font-size:18px; font-weight:800; color:#f87171;">{false_pos}</div>
                <div style="font-size:10px; color:#94a3b8;">False Positive</div>
            </div>
            <div style="text-align:center; padding:12px; background:rgba(245,158,11,0.1); border:1px solid #f59e0b; border-radius:8px; width:120px;">
                <div style="font-size:18px; font-weight:800; color:#fbbf24;">{false_neg}</div>
                <div style="font-size:10px; color:#94a3b8;">False Negative</div>
            </div>
            <div style="text-align:center; padding:12px; background:rgba(99,102,241,0.1); border:1px solid #6366f1; border-radius:8px; width:120px;">
                <div style="font-size:18px; font-weight:800; color:#818cf8;">{true_pos}</div>
                <div style="font-size:10px; color:#94a3b8;">True Fraud</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
