"""
Transaction input form component for the Streamlit dashboard.

Provides:
    - Manual transaction entry with validated inputs
    - Quick-fill presets for common scenarios (normal / suspicious / fraud)
    - Real-time input validation feedback
    - Premium card-based layout with section grouping
"""

import streamlit as st

from utils.constants import MERCHANT_CATEGORIES


def render_transaction_form() -> dict | None:
    """
    Render the transaction input form and return submitted data.

    Returns:
        Dict of transaction data if form was submitted, None otherwise.
    """
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <div style="
                width: 40px; height: 40px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 10px;
                background: rgba(99,102,241,0.12);
                border: 1px solid rgba(99,102,241,0.25);
                font-size: 20px;
            ">💳</div>
            <div>
                <div style="font-size: 16px; font-weight: 700; color: #e2e8f0;">
                    New Transaction
                </div>
                <div style="font-size: 12px; color: #64748b;">
                    Enter transaction details for real-time fraud analysis
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick-fill presets ────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
        ">SCENARIO PRESETS</div>
        """,
        unsafe_allow_html=True,
    )

    preset_cols = st.columns(3)

    with preset_cols[0]:
        if st.button("✅ Normal", use_container_width=True):
            st.session_state["preset"] = "normal"

    with preset_cols[1]:
        if st.button("⚠️ Suspicious", use_container_width=True):
            st.session_state["preset"] = "suspicious"

    with preset_cols[2]:
        if st.button("🚨 Likely Fraud", use_container_width=True):
            st.session_state["preset"] = "fraud"

    # Load preset values
    preset = st.session_state.get("preset", None)
    defaults = _get_preset_values(preset)

    st.markdown("---")

    # ── Form fields ───────────────────────────────────────────────────
    with st.form("transaction_form", clear_on_submit=False):

        # Payment Info Section
        st.markdown(
            """
            <div style="
                font-size: 11px; font-weight: 700;
                color: #64748b; letter-spacing: 1.5px;
                text-transform: uppercase; margin-bottom: 8px;
            ">💰 PAYMENT INFORMATION</div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Transaction Amount ($)",
                min_value=0.01,
                max_value=50000.00,
                value=defaults["amount"],
                step=10.0,
                format="%.2f",
                help="Must be between $0.01 and $50,000",
            )

            merchant_category = st.selectbox(
                "Merchant Category",
                options=MERCHANT_CATEGORIES,
                index=MERCHANT_CATEGORIES.index(defaults["merchant_category"]),
                format_func=lambda x: x.replace("_", " ").title(),
                help="Type of merchant where the transaction occurred",
            )

        with col2:
            avg_amount_30d = st.number_input(
                "30-Day Average Amount ($)",
                min_value=0.0,
                max_value=50000.0,
                value=defaults["avg_amount_30d"],
                step=10.0,
                format="%.2f",
                help="Average transaction amount over the last 30 days",
            )

            card_present = st.toggle(
                "💳 Card Present at POS",
                value=defaults["card_present"],
                help="Was the physical card present at the point of sale?",
            )

        # Context Section
        st.markdown(
            """
            <div style="
                font-size: 11px; font-weight: 700;
                color: #64748b; letter-spacing: 1.5px;
                text-transform: uppercase; margin: 16px 0 8px;
            ">📍 CONTEXT & LOCATION</div>
            """,
            unsafe_allow_html=True,
        )

        col3, col4 = st.columns(2)

        with col3:
            transaction_hour = st.slider(
                "Transaction Hour",
                min_value=0,
                max_value=23,
                value=defaults["transaction_hour"],
                help="Hour of day (0 = midnight, 23 = 11 PM)",
            )

            day_of_week = st.selectbox(
                "Day of Week",
                options=list(range(7)),
                index=defaults["day_of_week"],
                format_func=lambda x: [
                    "Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"
                ][x],
            )

        with col4:
            location_distance_km = st.number_input(
                "Distance from Home (km)",
                min_value=0.0,
                max_value=20000.0,
                value=defaults["location_distance_km"],
                step=5.0,
                help="Distance from cardholder's typical area",
            )

            is_international = st.toggle(
                "🌍 International Transaction",
                value=defaults["is_international"],
                help="Is this a cross-border transaction?",
            )

        # Velocity Section
        st.markdown(
            """
            <div style="
                font-size: 11px; font-weight: 700;
                color: #64748b; letter-spacing: 1.5px;
                text-transform: uppercase; margin: 16px 0 8px;
            ">⚡ VELOCITY SIGNALS</div>
            """,
            unsafe_allow_html=True,
        )

        velocity_last_1h = st.slider(
            "Transactions in Last Hour",
            min_value=0,
            max_value=30,
            value=defaults["velocity_last_1h"],
            help="Number of transactions by this cardholder in the last hour",
        )

        # ── Submit button ─────────────────────────────────────────────
        submitted = st.form_submit_button(
            "🔍  Analyze Transaction",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            # Clear preset after submission
            st.session_state.pop("preset", None)

            return {
                "amount": amount,
                "merchant_category": merchant_category,
                "transaction_hour": transaction_hour,
                "day_of_week": day_of_week,
                "location_distance_km": location_distance_km,
                "is_international": is_international,
                "card_present": card_present,
                "velocity_last_1h": velocity_last_1h,
                "avg_amount_30d": avg_amount_30d,
            }

    return None


def _get_preset_values(preset: str | None) -> dict:
    """Return default form values based on preset selection."""
    presets = {
        "normal": {
            "amount": 45.99,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 3.0,
            "is_international": False,
            "card_present": True,
            "velocity_last_1h": 1,
            "avg_amount_30d": 52.00,
        },
        "suspicious": {
            "amount": 890.00,
            "merchant_category": "electronics",
            "transaction_hour": 3,
            "day_of_week": 1,
            "location_distance_km": 250.0,
            "is_international": True,
            "card_present": False,
            "velocity_last_1h": 4,
            "avg_amount_30d": 85.00,
        },
        "fraud": {
            "amount": 4999.99,
            "merchant_category": "online_retail",
            "transaction_hour": 2,
            "day_of_week": 6,
            "location_distance_km": 3500.0,
            "is_international": True,
            "card_present": False,
            "velocity_last_1h": 12,
            "avg_amount_30d": 65.00,
        },
    }

    return presets.get(preset, presets["normal"])
