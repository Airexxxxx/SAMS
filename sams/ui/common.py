# ===================================================================
# SAMS - UI Common (CSS, helpers)
# ===================================================================

import streamlit as st

from sams.config import STATUS_LABELS


def inject_css():
    st.markdown("""
    <style>
    :root {
        --bg: #0f172a;
        --card: #1e293b;
        --border: #334155;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --primary: #3b82f6;
        --header-bg: #0b1120;
    }

    .stApp {
        background-color: #0f172a;
    }

    /* ===== HEADER ===== */
    .sams-header {
        background: linear-gradient(135deg, #0b1120 0%, #111f3a 100%);
        color: #e2e8f0;
        padding: 0 24px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 2px solid #3b82f6;
        margin: -16px -16px 0 -16px;
    }
    .sams-header .left {
        display: flex; align-items: center; gap: 12px;
        font-size: 18px; font-weight: 700; color: #f1f5f9;
    }
    .sams-header .right {
        display: flex; align-items: center; gap: 20px;
        font-size: 13px; color: #cbd5e1;
    }
    .sams-header .logo { font-size: 24px; }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
    }
    section[data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] button {
        color: #cbd5e1 !important;
        background-color: transparent !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] button:active,
    section[data-testid="stSidebar"] button:focus {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #1e293b !important;
    }

    /* ===== STATUS BADGES ===== */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        color: #fff;
    }
    .badge-running { background-color: #10b981; }
    .badge-stopped { background-color: #f59e0b; color: #1f2937; }
    .badge-maintenance { background-color: #3b82f6; }
    .badge-decommissioned { background-color: #ef4444; }

    /* ===== DETAIL DRAWER ===== */
    .detail-section {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid #1e293b;
        font-size: 13px;
    }
    .detail-label { color: #94a3b8; font-weight: 500; }
    .detail-value { color: #e2e8f0; font-weight: 600; text-align: right; max-width: 250px; }

    /* Hostname link in table */
    .hostname-link {
        color: #93c5fd !important;
        text-decoration: none;
        cursor: pointer;
        font-weight: 500;
    }
    .hostname-link:hover {
        color: #3b82f6 !important;
        text-decoration: underline;
    }

    /* ===== FOOTER ===== */
    .sams-footer {
        text-align: center; color: #475569; font-size: 12px;
        padding: 12px; border-top: 1px solid #1e293b; margin-top: 30px;
    }

    /* ===== INPUT FIELDS - ALWAYS VISIBLE BORDERS ===== */
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"] {
        border: 1px solid #475569 !important;
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 6px !important;
    }
    input:focus, textarea:focus, [data-baseweb="input"]:focus, [data-baseweb="textarea"]:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    [data-baseweb="select"] {
        border: 1px solid #475569 !important;
        background-color: #1e293b !important;
        border-radius: 6px !important;
    }
    [data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
    }
    [data-baseweb="popover"] {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
    }
    [data-baseweb="popover"] * {
        color: #e2e8f0 !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 6px; font-weight: 500;
        border: 1px solid #475569 !important;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
    }

    /* ===== EXPANDER / FORM ===== */
    .stExpander, [data-testid="stExpander"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stForm"] {
        background: transparent;
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        border-radius: 10px; overflow: hidden;
        border: 1px solid #334155;
    }
    [data-testid="stTable"] {
        color: #e2e8f0;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 28px !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6;
    }

    /* ===== ALERTS ===== */
    .stAlert {
        border-radius: 8px;
    }

    /* ===== MULTISELECT ===== */
    [data-baseweb="tag"] {
        background-color: #1e3a5f !important;
        border: 1px solid #3b82f6 !important;
        color: #e2e8f0 !important;
    }

    /* ===== NUMBER INPUT ===== */
    button[data-testid="stNumberInputButton"] {
        border: 1px solid #475569 !important;
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    return f'<span class="badge badge-{status}">{label}</span>'
