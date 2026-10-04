"""
AirAware — Main Streamlit App
Multi-Agent AI Air Quality Assistant (Zero API Keys)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import agents
from agents.orchestrator import Orchestrator
from utils.rag import load_knowledge_base
from utils.database import (
    init_db,
    create_report,
    get_all_reports,
    get_stats,
    get_recent_alerts,
)
from utils.mock_data import get_all_cities

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AirAware — AI Air Quality Assistant",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ecfeff 0%, #e0f2fe 50%, #dbeafe 100%);
    }
    h1 { color: #0e7490 !important; font-weight: 800 !important; }
    h2, h3 { color: #155e75 !important; font-weight: 700 !important; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e7490 0%, #155e75 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }

    .aqi-card {
        background: white;
        border-radius: 24px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 12px 40px rgba(14, 116, 144, 0.2);
        margin-bottom: 20px;
    }

    .aqi-value {
        font-size: 72px;
        font-weight: 900;
        line-height: 1;
        margin: 8px 0;
    }

    .aqi-label {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(14, 116, 144, 0.12);
        margin-bottom: 16px;
    }

    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(14, 116, 144, 0.1);
        border-left: 5px solid #06b6d4;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0e7490 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 15px;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(6, 182, 212, 0.5);
    }

    .status-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        color: white;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INIT
# ============================================================
init_db()
kb = load_knowledge_base()
orchestrator = Orchestrator(kb)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0;">
            <div style="font-size: 48px;">🌬️</div>
            <h2 style="color: white; font-size: 22px; margin: 8px 0;">AirAware</h2>
            <p style="color: #67e8f9; font-size: 12px; font-weight: 600;
                      letter-spacing: 0.1em;">AI AIR QUALITY ASSISTANT</p>
        </div>
        <hr style="border-color: rgba(103, 232, 249, 0.3);"/>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "**Navigation**",
        [
            "🏠 Live AQI",
            "🩺 Health Advisory",
            "🗺️ Route Planner",
            "📈 Trends",
            "🏫 Alerts",
        ],
    )

    st.markdown(
        '<hr style="border-color: rgba(103, 232, 249, 0.3);"/>',
        unsafe_allow_html=True,
    )

    city = st.selectbox(
        "🏙️ Select City",
        get_all_cities(),
        index=0,
    )

    st.markdown(
        """
        <hr style="border-color: rgba(103, 232, 249, 0.3);"/>
        <div style="padding: 10px 0; font-size: 12px; color: #67e8f9;">
            <p>✅ <b>Zero API Keys</b></p>
            <p>🧠 Multi-Agent + RAG</p>
            <p>🔒 100% Local AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPER
# ============================================================
def render_aqi_card(aqi_data: dict, level_info: dict):
    """Render big AQI card."""
    color = level_info.get("color_hex", "#64748b")
    level = level_info.get("level", "Unknown")

    st.markdown(
        f"""
        <div class="aqi-card">
            <div style="font-size: 14px; color: #64748b; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.1em;">
                {aqi_data['city']} — Live AQI
            </div>
            <div class="aqi-value" style="color: {color};">
                {aqi_data['aqi']}
            </div>
            <div class="aqi-label" style="color: {color};">
                {level}
            </div>
            <div style="margin-top: 16px; color: #64748b; font-size: 14px;">
                🌡️ {aqi_data['temperature']}°C &nbsp;|&nbsp;
                💧 {aqi_data['humidity']}% Humidity
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 1: LIVE AQI
# ============================================================
if page == "🏠 Live AQI":
    st.markdown("<h1>🏠 Live AQI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    aqi_data = orchestrator.aqi_agent.fetch(city)
    alerts = orchestrator.alert_agent.check(city, aqi_data["aqi"])

    col1, col2 = st.columns([2, 1])

    with col1:
        render_aqi_card(aqi_data, alerts)

    with col2:
        st.markdown("### 🚨 Quick Status")

        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #64748b;
                            text-transform: uppercase; font-weight: 600;">
                    😷 Mask
                </div>
                <div style="font-size: 18px; font-weight: 800; color: #0e7490;
                            margin-top: 8px;">
                    {alerts['mask_recommendation']}
                </div>
            </div>
            <br>
            <div class="metric-card">
                <div style="font-size: 12px; color: #64748b;
                            text-transform: uppercase; font-weight: 600;">
                    🏫 Schools
                </div>
                <div style="font-size: 16px; font-weight: 800;
                            color: {alerts['school_alert']['color']};
                            margin-top: 8px;">
                    {alerts['school_alert']['status']}
                </div>
            </div>
            <br>
            <div class="metric-card">
                <div style="font-size: 12px; color: #64748b;
                            text-transform: uppercase; font-weight: 600;">
                    🏃 Outdoor
                </div>
                <div style="font-size: 16px; font-weight: 800;
                            color: {alerts['color']}; margin-top: 8px;">
                    {alerts['outdoor_status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🧪 Pollutant Breakdown")

    pollutants = aqi_data["pollutants"]
    cols = st.columns(len(pollutants))

    for i, (name, value) in enumerate(pollutants.items()):
        with cols[i]:
            st.metric(
                label=name.upper(),
                value=f"{value}",
            )

    st.markdown("---")
    st.info(alerts["public_message"])


# ============================================================
# PAGE 2: HEALTH ADVISORY
# ============================================================
elif page == "🩺 Health Advisory":
    st.markdown("<h1>🩺 Personalized Health Advisory</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 👤 Your Profile")
        condition = st.selectbox(
            "Health Condition",
            [
                "Healthy Adult",
                "Asthma",
                "Heart Patient",
                "Pregnant Women",
                "Children",
                "Elderly",
            ],
        )

        aqi_data = orchestrator.aqi_agent.fetch(city)
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #64748b;
                            text-transform: uppercase;">
                    Current AQI in {city}
                </div>
                <div style="font-size: 42px; font-weight: 900;
                            color: #0e7490;">
                    {aqi_data['aqi']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### 💡 Your Personalized Advice")

        advice = orchestrator.health_agent.advise(aqi_data["aqi"], condition)

        risk_colors = {
            "Low": "#16a34a",
            "Moderate": "#eab308",
            "High": "#f97316",
            "Extreme": "#dc2626",
        }
        risk_color = risk_colors.get(advice["risk"], "#64748b")

        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 6px solid {risk_color};">
                <div style="display: flex; justify-content: space-between;
                            align-items: center; margin-bottom: 16px;">
                    <span style="font-weight: 700; color: #155e75;">
                        Risk Level
                    </span>
                    <span class="status-pill" style="background: {risk_color};">
                        {advice['risk']}
                    </span>
                </div>
                <p style="font-size: 16px; color: #0f172a; line-height: 1.6;">
                    {advice['summary']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_dos, col_donts = st.columns(2)

        with col_dos:
            st.markdown("#### ✅ Do's")
            for item in advice["dos"]:
                st.markdown(f"- {item}")

        with col_donts:
            st.markdown("#### ❌ Don'ts")
            for item in advice["donts"]:
                st.markdown(f"- {item}")

        st.markdown("---")
        st.markdown(f"**😷 Mask:** {advice['mask']}")


# ============================================================
# PAGE 3: ROUTE PLANNER
# ============================================================
elif page == "🗺️ Route Planner":
    st.markdown("<h1>🗺️ Smart Route Planner</h1>", unsafe_allow_html=True)
    st.markdown("Snap — find the least polluted route.", unsafe_allow_html=True)
    st.markdown("---")

    zones = ["Gulberg", "DHA", "Model Town", "Johar Town", "Saddar", "Clifton", "Blue Area", "F-7"]

    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("📍 Starting Zone", zones, index=0)
    with col2:
        end = st.selectbox("🎯 Destination Zone", zones, index=1)

    if st.button("🔍 Find Cleanest Route", type="primary"):
        with st.spinner("Planning routes..."):
            result = orchestrator.route_agent.plan(start, end, city)

        st.markdown("### 🛣️ Route Options")

        for route in result["routes"]:
            aqi = route["aqi"]
            if aqi < 100:
                color = "#16a34a"
                emoji = "✅"
            elif aqi < 200:
                color = "#eab308"
                emoji = "⚡"
            else:
                color = "#dc2626"
                emoji = "⚠️"

            is_best = route["name"] == result["recommended"]

            st.markdown(
                f"""
                <div class="glass-card" style="
                    border-left: 6px solid {color};
                    {'box-shadow: 0 12px 40px rgba(6, 182, 212, 0.4);' if is_best else ''}
                ">
                    <div style="display: flex; justify-content: space-between;
                                align-items: center;">
                        <div>
                            <div style="font-weight: 800; font-size: 18px;
                                        color: #0f172a;">
                                {emoji} {route['name']}
                                {'  🏆 RECOMMENDED' if is_best else ''}
                            </div>
                            <div style="color: #64748b; font-size: 13px;
                                        margin-top: 4px;">
                                {route['description']}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 28px; font-weight: 900;
                                        color: {color};">
                                {aqi}
                            </div>
                            <div style="font-size: 12px; color: #64748b;">
                                {route['distance']} km | {route['time']} min
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.info(result["advice"])


# ============================================================
# PAGE 4: TRENDS
# ============================================================
elif page == "📈 Trends":
    st.markdown("<h1>📈 Trends & Forecast</h1>", unsafe_allow_html=True)
    st.markdown("---")

    history = orchestrator.aqi_agent.history(city, days=30)
    forecast = orchestrator.aqi_agent.forecast(city, days=3)

    # 7-day trend
    st.markdown("### 📊 Last 7 Days")
    df7 = pd.DataFrame(history[-7:])
    fig = px.bar(
        df7, x="day", y="aqi",
        color="aqi",
        color_continuous_scale=["#16a34a", "#eab308", "#dc2626", "#991b1b"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 30-day line
    st.markdown("### 📈 Last 30 Days")
    df30 = pd.DataFrame(history)
    fig = px.line(df30, x="date", y="aqi", markers=True)
    fig.update_traces(line_color="#0e7490", line_width=3)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Forecast
    st.markdown("### 🔮 3-Day Forecast")
    df_fc = pd.DataFrame(forecast)

    cols = st.columns(3)
    for i, row in df_fc.iterrows():
        aqi = row["aqi"]
        if aqi < 100:
            color = "#16a34a"
        elif aqi < 200:
            color = "#eab308"
        else:
            color = "#dc2626"

        with cols[i]:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color: {color};">
                    <div style="font-size: 14px; color: #64748b;">
                        {row['day']}
                    </div>
                    <div style="font-size: 32px; font-weight: 900;
                                color: {color};">
                        {aqi}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 5: ALERTS
# ============================================================
elif page == "🏫 Alerts":
    st.markdown("<h1>🏫 Community Alerts & Reports</h1>", unsafe_allow_html=True)
    st.markdown("---")

    aqi_data = orchestrator.aqi_agent.fetch(city)
    alerts = orchestrator.alert_agent.check(city, aqi_data["aqi"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏫 School Alert")
        school = alerts["school_alert"]
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 6px solid {school['color']};">
                <div style="font-size: 24px; font-weight: 800;
                            color: {school['color']};">
                    {school['status']}
                </div>
                <p style="color: #0f172a; margin-top: 8px;">
                    {school['message']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### 🏢 Office Advisory")
        office = alerts["office_advisory"]
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 6px solid {office['color']};">
                <div style="font-size: 24px; font-weight: 800;
                            color: {office['color']};">
                    {office['status']}
                </div>
                <p style="color: #0f172a; margin-top: 8px;">
                    {office['message']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📢 Report a Pollution Issue")

    with st.form("report_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_zone = st.text_input("Zone / Area", placeholder="e.g. Gulberg")
            r_desc = st.text_area("Description", placeholder="Kya masla hai?")
        with c2:
            r_city = st.selectbox("City", get_all_cities())
            r_condition = st.selectbox("Concern", ["Smoke", "Dust", "Smell", "Traffic", "Other"])

        submitted = st.form_submit_button("📤 Submit Report")

        if submitted and r_zone and r_desc:
            aqi_data_r = orchestrator.aqi_agent.fetch(r_city)
            report_id = create_report(
                r_zone, r_city, aqi_data_r["aqi"], r_condition, r_desc
            )
            st.success(f"✅ Report submitted! ID: {report_id}")

    st.markdown("---")
    st.markdown("### 📋 Recent Reports")

    reports = get_all_reports()
    if reports:
        df = pd.DataFrame(reports)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Abhi tak koi report nahi aayi.")
