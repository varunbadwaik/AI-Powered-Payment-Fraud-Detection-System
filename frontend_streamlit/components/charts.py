"""
Professional Plotly chart components for the banking fraud dashboard.

All charts use a cohesive dark premium theme with glassmorphism
accents and a consistent color system.
"""

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd


# ── Shared theme settings ─────────────────────────────────────────────
CHART_TEMPLATE = "plotly_dark"
COLOR_PALETTE = {
    "Low": "#10b981",
    "Medium": "#f59e0b",
    "High": "#ef4444",
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "accent": "#06b6d4",
    "bg": "#0f172a",
    "card_bg": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#64748b",
}

LAYOUT_DEFAULTS = dict(
    template=CHART_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLOR_PALETTE["text"], size=12),
    margin=dict(l=40, r=40, t=56, b=40),
)


def render_risk_distribution_chart(risk_distribution: dict) -> None:
    """
    Donut chart showing the distribution of Low / Medium / High risk transactions.

    Args:
        risk_distribution: Dict like {"Low": 450, "Medium": 30, "High": 10}
    """
    if not risk_distribution:
        st.info("No data available for risk distribution.")
        return

    labels = list(risk_distribution.keys())
    values = list(risk_distribution.values())
    colors = [COLOR_PALETTE.get(label, "#64748b") for label in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#0f172a", width=3)),
                textinfo="label+percent",
                textfont=dict(size=13, family="Inter, sans-serif"),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Risk Level Distribution</b>",
            font=dict(size=16),
            x=0.02,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        height=380,
        annotations=[
            dict(
                text=f"<b>{sum(values)}</b><br><span style='font-size:11px;color:#64748b'>Total</span>",
                showarrow=False,
                font=dict(size=22, color="#e2e8f0"),
                x=0.5,
                y=0.5,
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True)


def render_fraud_score_histogram(transactions: list[dict]) -> None:
    """
    Histogram of fraud probability scores across all transactions.

    Args:
        transactions: List of transaction dicts with 'fraud_probability' key.
    """
    if not transactions:
        st.info("No transaction data available.")
        return

    scores = [t.get("fraud_probability", 0) for t in transactions]

    fig = go.Figure(
        data=[
            go.Histogram(
                x=scores,
                nbinsx=30,
                marker=dict(
                    color=COLOR_PALETTE["primary"],
                    line=dict(color=COLOR_PALETTE["secondary"], width=1),
                ),
                opacity=0.85,
                hovertemplate="Score range: %{x}<br>Count: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>Fraud Score Distribution</b>", font=dict(size=16), x=0.02),
        xaxis_title="Fraud Probability",
        yaxis_title="Number of Transactions",
        height=380,
        bargap=0.05,
    )

    # Add threshold lines
    fig.add_vline(
        x=0.3,
        line_dash="dash",
        line_color="#10b981",
        line_width=1.5,
        annotation_text="Low / Med",
        annotation_position="top",
        annotation_font=dict(size=10, color="#10b981"),
    )
    fig.add_vline(
        x=0.7,
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text="Med / High",
        annotation_position="top",
        annotation_font=dict(size=10, color="#ef4444"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_feature_importance_chart(importance: dict) -> None:
    """
    Horizontal bar chart of global feature importance.

    Args:
        importance: Dict of feature_name → importance_score.
    """
    if not importance:
        st.info("Feature importance data not available.")
        return

    features = list(importance.keys())
    scores = list(importance.values())

    # Sort by importance
    sorted_pairs = sorted(zip(scores, features))
    scores, features = zip(*sorted_pairs)

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(scores),
                y=list(features),
                orientation="h",
                marker=dict(
                    color=list(scores),
                    colorscale=[[0, "#6366f1"], [0.5, "#8b5cf6"], [1, "#ef4444"]],
                    line=dict(width=0),
                    cornerradius=4,
                ),
                hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>Feature Importance (Global)</b>", font=dict(size=16), x=0.02),
        xaxis_title="Importance Score",
        yaxis_title="",
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_transaction_timeline(transactions: list[dict]) -> None:
    """
    Line chart showing fraud scores over time.

    Args:
        transactions: List of transaction dicts with 'fraud_probability' and 'created_at'.
    """
    if not transactions:
        st.info("No timeline data available.")
        return

    timestamps = [t.get("created_at", "") for t in transactions]
    scores = [t.get("fraud_probability", 0) for t in transactions]
    risk_colors = [
        COLOR_PALETTE.get(t.get("risk_level", "Low"), "#64748b")
        for t in transactions
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=scores,
            mode="lines+markers",
            line=dict(color=COLOR_PALETTE["accent"], width=2.5, shape="spline"),
            marker=dict(
                color=risk_colors,
                size=9,
                line=dict(width=2, color="#0f172a"),
            ),
            fill="tozeroy",
            fillcolor="rgba(6,182,212,0.06)",
            hovertemplate="<b>%{x}</b><br>Score: %{y:.4f}<extra></extra>",
        )
    )

    # Add risk threshold zones
    fig.add_hrect(y0=0, y1=0.3, fillcolor="#10b981", opacity=0.04, line_width=0)
    fig.add_hrect(y0=0.3, y1=0.7, fillcolor="#f59e0b", opacity=0.04, line_width=0)
    fig.add_hrect(y0=0.7, y1=1.0, fillcolor="#ef4444", opacity=0.04, line_width=0)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>Transaction Risk Timeline</b>", font=dict(size=16), x=0.02),
        xaxis_title="Time",
        yaxis_title="Fraud Probability",
        yaxis=dict(range=[0, 1]),
        height=380,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_amount_vs_risk_scatter(transactions: list[dict]) -> None:
    """
    Scatter plot showing transaction amount vs fraud probability.

    Args:
        transactions: List of transaction dicts.
    """
    if not transactions:
        st.info("No data available for scatter plot.")
        return

    amounts = [t.get("amount", 0) for t in transactions]
    scores = [t.get("fraud_probability", 0) for t in transactions]
    risk_levels = [t.get("risk_level", "Low") for t in transactions]
    colors = [COLOR_PALETTE.get(r, "#64748b") for r in risk_levels]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=amounts,
                y=scores,
                mode="markers",
                marker=dict(
                    color=colors,
                    size=11,
                    opacity=0.8,
                    line=dict(width=1.5, color="#0f172a"),
                ),
                hovertemplate="Amount: $%{x:,.2f}<br>Fraud Score: %{y:.4f}<extra></extra>",
            )
        ]
    )

    # Add quadrant labels
    fig.add_hrect(y0=0.7, y1=1.0, fillcolor="#ef4444", opacity=0.04, line_width=0)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>Amount vs Risk Score</b>", font=dict(size=16), x=0.02),
        xaxis_title="Amount ($)",
        yaxis_title="Fraud Probability",
        yaxis=dict(range=[0, 1]),
        height=380,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_transaction_table(transactions: list[dict]) -> None:
    """
    Render a premium transaction table using pandas + Streamlit dataframe
    with a styled header card. Reliable rendering at any row count.

    Args:
        transactions: List of transaction dicts from the API.
    """
    if not transactions:
        _render_empty_table()
        return

    # Table header card
    st.markdown(f"""<div style="background:#1e293b;border:1px solid #334155;border-radius:16px 16px 0 0;padding:16px 20px;display:flex;align-items:center;justify-content:space-between;">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.2);font-size:16px;">📋</div>
<span style="font-size:15px;font-weight:700;color:#e2e8f0;">Transaction Ledger</span>
</div>
<span style="font-size:12px;color:#64748b;background:#0f172a;padding:4px 12px;border-radius:20px;font-weight:600;">{len(transactions)} records</span>
</div>""", unsafe_allow_html=True)

    # Build DataFrame
    import pandas as pd

    rows = []
    for txn in transactions[:50]:
        risk = txn.get("risk_level", "Low")
        score = txn.get("fraud_probability", 0)
        actions_map = {"Low": "✅ Approved", "Medium": "👁️ Review", "High": "🚫 Blocked"}
        risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

        rows.append({
            "TXN ID": txn.get("transaction_id", "—"),
            "Amount ($)": txn.get("amount", 0),
            "Category": txn.get("merchant_category", "—").replace("_", " ").title(),
            "Risk Score": round(score, 4),
            "Status": f"{risk_emoji.get(risk, '')} {risk}",
            "Action": actions_map.get(risk, "—"),
            "Timestamp": txn.get("created_at", "—"),
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        height=480,
        column_config={
            "TXN ID": st.column_config.TextColumn("TXN ID", width="medium"),
            "Amount ($)": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score",
                min_value=0,
                max_value=1,
                format="%.1%%",
            ),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Action": st.column_config.TextColumn("Action", width="small"),
            "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
        },
        hide_index=True,
    )

    # Per-row risk badge cards for high-risk items
    high_risk = [t for t in transactions if t.get("risk_level") == "High"]
    if high_risk:
        st.markdown(f"""<div style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.5px;margin:16px 0 8px;">🔴 HIGH-RISK TRANSACTIONS ({len(high_risk)})</div>""", unsafe_allow_html=True)
        for txn in high_risk[:5]:
            _render_risk_row_card(txn)


def _render_risk_row_card(txn: dict) -> None:
    """Render a compact risk card for a single flagged transaction."""
    txn_id = txn.get("transaction_id", "—")
    amount = txn.get("amount", 0)
    score = txn.get("fraud_probability", 0)
    risk = txn.get("risk_level", "High")
    bc = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}.get(risk, "#ef4444")

    st.markdown(f"""<div style="background:#1e293b;border-left:4px solid {bc};border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
<div>
<span style="font-family:monospace;font-size:12px;color:#818cf8;background:rgba(99,102,241,0.1);padding:2px 8px;border-radius:4px;">{txn_id}</span>
<span style="color:#e2e8f0;font-weight:600;margin-left:12px;">${amount:,.2f}</span>
</div>
<div>
<span style="font-size:12px;font-weight:700;color:{bc};margin-right:8px;">{score:.1%}</span>
<span style="display:inline-block;padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);">BLOCKED</span>
</div></div>""", unsafe_allow_html=True)


def _render_empty_table() -> None:
    """Render an empty state placeholder for the transaction table."""
    st.markdown("""<div style="background:#1e293b;border:1px solid #334155;border-radius:16px;padding:60px 40px;text-align:center;">
<div style="font-size:48px;margin-bottom:12px;opacity:0.4;">📋</div>
<div style="font-size:16px;color:#64748b;font-weight:500;">No transactions recorded yet</div>
<div style="font-size:13px;color:#475569;margin-top:6px;">Analyze some transactions to populate the ledger</div>
</div>""", unsafe_allow_html=True)
