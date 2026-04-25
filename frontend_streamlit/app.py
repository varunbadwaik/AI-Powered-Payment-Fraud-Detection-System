"""
Premium BankOS-Style AI Fraud Detection Dashboard.
Single-page Streamlit application focused on real-time transaction monitoring.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils.config import settings

# ── Backend Communication ───────────────────────────────────────────────
BACKEND_URL = settings.BACKEND_URL

def api_predict(transaction_data: dict) -> dict | None:
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/predict", json=transaction_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None

def api_get_transactions(limit: int = 50) -> list[dict]:
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/transactions", params={"limit": limit}, timeout=10)
        r.raise_for_status()
        return r.json().get("transactions", [])
    except Exception:
        return []

# ── Page Configuration ──────────────────────────────────────────────────
st.set_page_config(page_title="Fraud Detection", page_icon="🛡️", layout="wide")

# ── Custom Premium Styling ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark Theme & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Page Title styling */
    .title-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 5px;
    }
    .title-icon {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        font-weight: 800;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* Top Header Adjustments */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .metric-label {
        font-size: 14px !important;
        color: #8b949e !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #f0f6fc !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
    }

    /* Dataframes */
    .stDataFrame {
        background: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
        overflow: hidden;
    }

    /* Requested Dark Theme Cards */
    .card {
        background-color: #161B22;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    .metric {
        font-size: 36px;
        font-weight: bold;
        margin-top: 5px;
    }
    .green {color: #00FF9C;}
    .orange {color: #FFA500;}
    .red {color: #FF4B4B;}
</style>
""", unsafe_allow_html=True)

# ── Color Badges Helper ─────────────────────────────────────────────────
def get_color(risk):
    if risk == "High": return "red"
    elif risk == "Medium": return "orange"
    return "green"

def risk_badge(risk):
    if risk == "High": return "🔴 High"
    elif risk == "Medium": return "🟠 Medium"
    return "🟢 Low"

# ======================================================================
#  HEADER
# ======================================================================
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.markdown("""
        <div class='title-wrapper'>
            <span class='title-icon'>⬡</span>
            <h1 style='margin:0; padding:0; font-size:32px; font-weight:800;'>Fraud Detection Engine</h1>
        </div>
        <p style='color:#8b949e; font-size:15px; margin-top:0px;'>Real-time transaction monitoring & risk assessment</p>
    """, unsafe_allow_html=True)
with head_col2:
    st.markdown("<div style='text-align:right; margin-top:20px;'><span style='background:#1f2937; padding:8px 16px; border-radius:20px; font-weight:600; font-size:14px; border:1px solid #374151;'><span style='color:#2ea043;'>●</span> System Active</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #30363d; opacity: 0.5; margin-top:0px;'>", unsafe_allow_html=True)

# ======================================================================
#  SIDEBAR (TRANSACTION INPUT)
# ======================================================================
st.sidebar.markdown("<h2 style='font-size:20px; font-weight:700; margin-bottom:0px;'>Transaction Input</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#8b949e; font-size:13px; margin-bottom:20px;'>Simulate a transaction to evaluate risk</p>", unsafe_allow_html=True)

# Collect inputs
amount = st.sidebar.number_input("Amount ($)", min_value=0.01, value=150.00, step=10.0)

MERCHANT_MAP = {
    "Online Retail": "online_retail",
    "Grocery": "grocery",
    "Electronics": "electronics",
    "Restaurant": "restaurant",
    "Travel": "travel",
    "ATM Withdrawal": "atm_withdrawal"
}
location = st.sidebar.selectbox("Location / Merchant Type", list(MERCHANT_MAP.keys()))
time = st.sidebar.slider("Transaction Hour", 0, 23, 14)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
predict_btn = st.sidebar.button("Evaluate Risk")

# ======================================================================
#  MAIN LAYOUT
# ======================================================================
risk_score = 0.0
risk_label = "Low"
txn_processed = False

if predict_btn:
    # Map visual inputs to backend API expectations
    data = {
        "amount": float(amount),
        "merchant_category": MERCHANT_MAP[location],
        "transaction_hour": int(time),
        "day_of_week": 3,  # Default to Wednesday
        "location_distance_km": 5.0,
        "is_international": False,
        "card_present": False if location == "Online Retail" else True,
        "velocity_last_1h": 1,
        "avg_amount_30d": 120.0
    }
    
    with st.spinner("Analyzing risk profile..."):
        result = api_predict(data)
        if result:
            risk_score = result.get("fraud_probability", 0.0) * 100  # Scale to 0-100
            risk_label = result.get("risk_level", "Low")
            txn_processed = True

# ---------- RISK CARDS ----------
st.markdown("<h3 style='margin-bottom:15px; font-size:18px;'>Live Risk Assessment</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

def get_color_class(risk):
    if risk == "High": return "red"
    elif risk == "Medium": return "orange"
    return "green"

color_class = get_color_class(risk_label)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Risk Score</div>
        <div class="metric">{risk_score:.2f}/100</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Risk Level</div>
        <div class="metric {color_class}">{risk_label}</div>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    color_hex = {"red": "#FF4B4B", "orange": "#FFA500", "green": "#00FF9C"}.get(color_class, "#8b949e")
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Engine Status</div>
        <div style='display:flex; align-items:center; gap:12px; margin-top:8px;'>
            <div style='width:16px; height:16px; border-radius:50%; background-color:{color_hex}; box-shadow: 0 0 15px {color_hex};'></div>
            <span style='font-size:32px; font-weight:700;' class="{color_class}">{risk_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- ALERT ----------
if txn_processed:
    if risk_label == "High":
        msg = "🚨 HIGH RISK TRANSACTION DETECTED. Immediate block applied."
        border_col = "#FF4B4B"
    elif risk_label == "Medium":
        msg = "⚠️ MEDIUM RISK TRANSACTION. Escalated for manual review."
        border_col = "#FFA500"
    else:
        msg = "✅ SAFE TRANSACTION. No anomalous behavior detected."
        border_col = "#00FF9C"
        
    st.markdown(f"""
        <div class="card" style="border-left: 4px solid {border_col}; margin-bottom: 24px; display: flex; align-items: center;">
            <span class="{color_class}" style="font-weight: 600; font-size: 16px;">{msg}</span>
        </div>
    """, unsafe_allow_html=True)

# ---------- CHARTS ----------
st.markdown("<h3 style='margin-bottom:15px; font-size:18px;'>Network Analytics</h3>", unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns([2, 1])

# Fetch recent transactions
recent_txns = api_get_transactions(limit=100)
if not recent_txns:
    # Dummy data if no backend transactions yet
    df_txns = pd.DataFrame({
        "Amount": [120, 5000, 230, 9000, 45, 800, 1500, 30],
        "Risk": ["Low", "High", "Low", "High", "Low", "Medium", "Medium", "Low"],
        "Location": ["NY", "Unknown", "CA", "International", "TX", "FL", "NY", "WA"],
        "Time": pd.date_range(start="2026-04-25 08:00", periods=8, freq="H")
    })
else:
    # Convert backend data to dataframe
    df_txns = pd.DataFrame([{
        "Amount": t.get("amount", 0),
        "Risk": t.get("risk_level", "Low"),
        "Location": t.get("merchant", "Unknown"),
        "Time": t.get("timestamp", datetime.now().isoformat())
    } for t in recent_txns])
    df_txns["Time"] = pd.to_datetime(df_txns["Time"])

with chart_col1:
    # Line chart (Transaction volume/amount over time)
    st.markdown("<div style='background:#161b22; padding:20px; border-radius:12px; border:1px solid #30363d;'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label' style='margin-bottom:10px;'>Transaction Volume (Amount over Time)</div>", unsafe_allow_html=True)
    
    # Simple line chart using plotly
    fig_line = px.line(
        df_txns.sort_values("Time"), 
        x="Time", 
        y="Amount", 
        color="Risk",
        color_discrete_map={"Low": "#2ea043", "Medium": "#d29922", "High": "#f85149"},
        markers=True
    )
    fig_line.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor="#30363d", title=""),
        yaxis=dict(showgrid=True, gridcolor="#30363d", title="Amount ($)")
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    # Donut Chart (Fraud vs Normal)
    st.markdown("<div style='background:#161b22; padding:20px; border-radius:12px; border:1px solid #30363d; height: 100%;'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label' style='margin-bottom:10px;'>Risk Distribution</div>", unsafe_allow_html=True)
    
    risk_counts = df_txns["Risk"].value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]
    
    fig_pie = px.pie(
        risk_counts, 
        values="Count", 
        names="Risk", 
        hole=0.6,
        color="Risk",
        color_discrete_map={"Low": "#2ea043", "Medium": "#d29922", "High": "#f85149"}
    )
    fig_pie.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- TABLE ----------
st.markdown("<h3 style='margin-bottom:15px; font-size:18px;'>Recent Transactions Ledger</h3>", unsafe_allow_html=True)

# Apply styling to dataframe
def apply_risk_style(val):
    if val == "High": return "color: #f85149; font-weight: bold;"
    elif val == "Medium": return "color: #d29922; font-weight: bold;"
    return "color: #2ea043;"

styled_df = df_txns.sort_values("Time", ascending=False).head(20).copy()
styled_df["Time"] = styled_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
styled_df["Amount"] = styled_df["Amount"].apply(lambda x: f"${x:,.2f}")

st.dataframe(
    styled_df.style.map(apply_risk_style, subset=["Risk"]),
    use_container_width=True,
    hide_index=True
)
