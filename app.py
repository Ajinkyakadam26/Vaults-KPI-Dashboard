# ══════════════════════════════════════════════════════════
# VaultX KPI Intelligence Dashboard — Home Page
# Author: Ajinkya Kadam
# Stack: Python, DuckDB, Streamlit, Plotly
# ══════════════════════════════════════════════════════════

import streamlit as st
from utils import load_data, apply_filters, render_filters, kpi_card, format_number

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="VaultX KPI Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Light theme custom CSS ─────────────────────────────────
st.markdown("""
    <style>
        /* Main background */
        .stApp { background-color: #F8FAFC; }

        /* Hide default streamlit header */
        header[data-testid="stHeader"] { background: transparent; }

        /* Top nav bar */
        .nav-bar {
            background: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            padding: 14px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
        }

        .nav-logo {
            font-size: 22px;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.5px;
        }

        .nav-logo span { color: #3B82F6; }

        .nav-links {
            display: flex;
            gap: 24px;
        }

        .nav-link {
            font-size: 14px;
            color: #64748B;
            text-decoration: none;
            font-weight: 500;
        }

        /* Hero section */
        .hero-section {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
            border-radius: 16px;
            padding: 48px 40px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(59,130,246,0.2);
            border: 1px solid rgba(59,130,246,0.4);
            color: #93C5FD;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            padding: 5px 14px;
            border-radius: 20px;
            margin-bottom: 16px;
        }

        .hero-title {
            font-size: 42px;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.1;
            margin-bottom: 12px;
        }

        .hero-title span { color: #3B82F6; }

        .hero-sub {
            font-size: 16px;
            color: #94A3B8;
            margin-bottom: 24px;
            max-width: 600px;
        }

        .hero-tags {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .hero-tag {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: #CBD5E1;
            font-size: 12px;
            padding: 5px 12px;
            border-radius: 20px;
        }

        /* Section title */
        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 16px;
        }

        /* Page cards */
        .page-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 28px;
            height: 100%;
            transition: box-shadow 0.2s;
        }

        .page-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        .page-card-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .page-card-title {
            font-size: 17px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 8px;
        }

        .page-card-desc {
            font-size: 13px;
            color: #64748B;
            line-height: 1.6;
        }

        .page-card-metrics {
            margin-top: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .metric-pill {
            display: inline-block;
            background: #F1F5F9;
            color: #475569;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 20px;
            margin-right: 4px;
            margin-bottom: 4px;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 32px 0 16px;
            color: #94A3B8;
            font-size: 12px;
            border-top: 1px solid #E2E8F0;
            margin-top: 48px;
        }

        /* Remove streamlit padding */
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────
df = load_data()

# ── Hero section ───────────────────────────────────────────
st.markdown("""
    <div class='hero-section'>
        <div class='hero-badge'>KPI Intelligence Platform</div>
        <div class='hero-title'>Vault<span>X</span> Analytics</div>
        <div class='hero-sub'>
            Real-time KPI monitoring across Products, Revenue, and Growth
            for a fictional fintech super-app with 1,000,000 transactions.
        </div>
        <div class='hero-tags'>
            <span class='hero-tag'>🐍 Python</span>
            <span class='hero-tag'>🦆 DuckDB</span>
            <span class='hero-tag'>📊 Streamlit</span>
            <span class='hero-tag'>📈 Plotly</span>
            <span class='hero-tag'>🗄️ 1M Rows</span>
            <span class='hero-tag'>📅 Jan 2024 — Jun 2026</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── Top filters ────────────────────────────────────────────
st.markdown("<div class='section-title'>🔍 Filters</div>", unsafe_allow_html=True)
products, regions, channels, date_range = render_filters(df)
filtered_df = apply_filters(df, products, regions, channels, date_range)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────
st.markdown("<div class='section-title'>📊 Overall KPIs</div>", unsafe_allow_html=True)

total_revenue    = filtered_df['revenue'].sum()
total_spend      = filtered_df['spend'].sum()
avg_roas         = filtered_df['roas'].mean()
avg_arpu         = filtered_df['arpu'].mean()
avg_nps          = filtered_df['nps_score'].mean()
total_users      = filtered_df['user_id'].nunique()
dau_count        = filtered_df[filtered_df['dau_flag'] == True]['user_id'].nunique()
mau_count        = filtered_df[filtered_df['mau_flag'] == True]['user_id'].nunique()
dau_mau_ratio    = dau_count / mau_count if mau_count > 0 else 0
churn_risk_count = filtered_df[filtered_df['churn_risk'] == True].shape[0]

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    kpi_card("Total Revenue", format_number(total_revenue))
with col2:
    kpi_card("Avg ROAS", f"{avg_roas:.2f}x")
with col3:
    kpi_card("Avg ARPU", format_number(avg_arpu))
with col4:
    kpi_card("DAU / MAU Ratio", f"{dau_mau_ratio:.2f}")
with col5:
    kpi_card("Avg NPS Score", f"{avg_nps:.1f} / 10")

st.markdown("<br>", unsafe_allow_html=True)

# ── Page Navigation Cards ──────────────────────────────────
st.markdown("<div class='section-title'>📂 Dashboard Pages</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class='page-card'>
            <div class='page-card-icon'>📱</div>
            <div class='page-card-title'>Product & Growth View</div>
            <div class='page-card-desc'>
                Tracks user engagement, product stickiness, funnel
                conversion, NPS scores, and new vs returning user trends
                across all 4 VaultX products.
            </div>
            <div class='page-card-metrics'>
                <span class='metric-pill'>DAU / MAU Ratio</span>
                <span class='metric-pill'>Conversion Funnel</span>
                <span class='metric-pill'>NPS by Product</span>
                <span class='metric-pill'>Monthly Active Users</span>
                <span class='metric-pill'>Device Split</span>
                <span class='metric-pill'>New vs Returning</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='page-card'>
            <div class='page-card-icon'>💰</div>
            <div class='page-card-title'>Revenue & Risk View</div>
            <div class='page-card-desc'>
                Monitors ARPU by product, regional ROAS performance,
                month-over-month revenue growth, and high churn risk
                users across all channels and regions.
            </div>
            <div class='page-card-metrics'>
                <span class='metric-pill'>ARPU by Product</span>
                <span class='metric-pill'>Regional ROAS Heatmap</span>
                <span class='metric-pill'>MoM Revenue Growth</span>
                <span class='metric-pill'>Revenue by Region</span>
                <span class='metric-pill'>Channel ROAS</span>
                <span class='metric-pill'>Churn Risk Table</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────
st.markdown("""
    <div class='footer'>
        Designed by Ajinkya Kadam &nbsp;|&nbsp;
        Built with Python, DuckDB, Streamlit & Plotly &nbsp;|&nbsp;
        VaultX is a fictional fintech platform
    </div>
""", unsafe_allow_html=True)
