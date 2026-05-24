# ══════════════════════════════════════════════════════════
# VaultX KPI Intelligence Dashboard — Utils
# Author: Ajinkya Kadam
# Purpose: Shared functions used across all pages
# ══════════════════════════════════════════════════════════

import duckdb
import pandas as pd
import streamlit as st


# ── Load data (cached so it only loads once) ───────────────
@st.cache_data
def load_data():
    df = pd.read_csv('vaultx_data.csv', parse_dates=['date'])
    return df


# ── Run any DuckDB query on the dataframe ──────────────────
def run_query(query: str, df: pd.DataFrame) -> pd.DataFrame:
    conn = duckdb.connect()
    conn.register('vaultx_data', df)
    result = conn.execute(query).fetchdf()
    conn.close()
    return result


# ── Apply filters and return filtered dataframe ────────────
def apply_filters(df: pd.DataFrame,
                  products: list,
                  regions: list,
                  channels: list,
                  date_range: tuple) -> pd.DataFrame:

    filtered = df.copy()

    if products:
        filtered = filtered[filtered['product'].isin(products)]

    if regions:
        filtered = filtered[filtered['region'].isin(regions)]

    if channels:
        filtered = filtered[filtered['channel'].isin(channels)]

    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered['date'] >= pd.Timestamp(date_range[0])) &
            (filtered['date'] <= pd.Timestamp(date_range[1]))
        ]

    return filtered


# ── Render top filter bar with dropdowns + Apply button ────
def render_filters(df: pd.DataFrame):

    st.markdown("""
        <style>
            div[data-testid="stForm"] {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 16px 20px;
            }
            /* Filter labels */
            div[data-testid="stForm"] label p {
                color: #0F172A !important;
                font-size: 13px !important;
                font-weight: 600 !important;
            }
            /* Multiselect container */
            div[data-testid="stForm"] .stMultiSelect [data-baseweb="select"] {
                background-color: #F8FAFC !important;
                border-color: #E2E8F0 !important;
            }
            /* Selected value pills */
            div[data-testid="stForm"] .stMultiSelect span[data-baseweb="tag"] {
                background-color: #EFF6FF !important;
                border: 1px solid #BFDBFE !important;
            }
            /* Pill text */
            div[data-testid="stForm"] .stMultiSelect span[data-baseweb="tag"] span {
                color: #1D4ED8 !important;
            }
            /* X button on pill */
            div[data-testid="stForm"] .stMultiSelect span[data-baseweb="tag"] button {
                color: #1D4ED8 !important;
                background: transparent !important;
                margin-top: 0 !important;
                width: auto !important;
            }
            /* Apply button */
            div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
                background-color: #3B82F6 !important;
                color: white !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                width: 100% !important;
                margin-top: 22px !important;
                border: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.form(key='filter_form'):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

        with col1:
            selected_products = st.multiselect(
                '🛍️ Product',
                options=sorted(df['product'].unique()),
                default=sorted(df['product'].unique()),
                placeholder='Select products...'
            )

        with col2:
            selected_regions = st.multiselect(
                '🌍 Region',
                options=sorted(df['region'].unique()),
                default=sorted(df['region'].unique()),
                placeholder='Select regions...'
            )

        with col3:
            selected_channels = st.multiselect(
                '📡 Channel',
                options=sorted(df['channel'].unique()),
                default=sorted(df['channel'].unique()),
                placeholder='Select channels...'
            )

        with col4:
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            selected_dates = st.date_input(
                '📅 Date Range',
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

        with col5:
            st.form_submit_button(
                '✅ Apply',
                use_container_width=True
            )

    return selected_products, selected_regions, selected_channels, selected_dates


# ── KPI card styling ───────────────────────────────────────
def kpi_card(label: str, value: str, delta: str = None):
    delta_html = f"<p style='color:#10B981; font-size:13px; margin:0;'>{delta}</p>" if delta else ""
    st.markdown(f"""
        <div style='
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        '>
            <p style='
                color: #64748B;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            '>{label}</p>
            <p style='
                color: #0F172A;
                font-size: 26px;
                font-weight: 700;
                margin: 0;
            '>{value}</p>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


# ── Format large numbers ───────────────────────────────────
def format_number(n: float) -> str:
    if n >= 1_000_000_000:
        return f"₹{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"₹{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"₹{n/1_000:.1f}K"
    else:
        return f"₹{n:.0f}"


# ── Light theme chart config ───────────────────────────────
CHART_THEME = {
    'bg_color':      '#FFFFFF',
    'paper_color':   '#F8FAFC',
    'font_color':    '#0F172A',
    'grid_color':    '#E2E8F0',
    'accent_colors': [
        '#3B82F6',
        '#10B981',
        '#F59E0B',
        '#EF4444',
        '#8B5CF6',
    ]
}
