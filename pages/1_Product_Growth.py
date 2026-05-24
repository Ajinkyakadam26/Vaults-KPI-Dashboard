# ══════════════════════════════════════════════════════════
# VaultX KPI Intelligence Dashboard — Product & Growth View
# Author: Ajinkya Kadam
# ══════════════════════════════════════════════════════════

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, apply_filters, render_filters, kpi_card, format_number, run_query

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Product & Growth — VaultX",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Light theme CSS ────────────────────────────────────────
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        .block-container { padding-top: 1rem; }
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 12px;
            margin-top: 28px;
            padding-bottom: 8px;
            border-bottom: 2px solid #E2E8F0;
        }
        .page-header {
            background: linear-gradient(135deg, #1E3A5F 0%, #0F172A 100%);
            border-radius: 14px;
            padding: 28px 32px;
            margin-bottom: 24px;
        }
        .page-header-title {
            font-size: 28px;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 6px;
        }
        .page-header-sub {
            font-size: 14px;
            color: #94A3B8;
        }
    </style>
""", unsafe_allow_html=True)

# ── Load and filter data ───────────────────────────────────
df = load_data()

# ── Page header ────────────────────────────────────────────
st.markdown("""
    <div class='page-header'>
        <div class='page-header-title'>📱 Product & Growth View</div>
        <div class='page-header-sub'>
            User engagement, product stickiness, funnel conversion and NPS across all VaultX products
        </div>
    </div>
""", unsafe_allow_html=True)

# ── Top filters ────────────────────────────────────────────
st.markdown("<div class='section-title'>🔍 Filters</div>", unsafe_allow_html=True)
products, regions, channels, date_range = render_filters(df)
filtered_df = apply_filters(df, products, regions, channels, date_range)

# ── KPI Cards ──────────────────────────────────────────────
st.markdown("<div class='section-title'>📊 Product KPIs</div>", unsafe_allow_html=True)

total_users   = filtered_df['user_id'].nunique()
dau_count     = filtered_df[filtered_df['dau_flag'] == True]['user_id'].nunique()
mau_count     = filtered_df[filtered_df['mau_flag'] == True]['user_id'].nunique()
dau_mau_ratio = dau_count / mau_count if mau_count > 0 else 0
avg_nps       = filtered_df['nps_score'].mean()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    kpi_card("Total Users", f"{total_users:,}")
with col2:
    kpi_card("DAU", f"{dau_count:,}")
with col3:
    kpi_card("MAU", f"{mau_count:,}")
with col4:
    kpi_card("DAU / MAU Ratio", f"{dau_mau_ratio:.2f}")
with col5:
    kpi_card("Avg NPS Score", f"{avg_nps:.1f} / 10")

st.markdown("<br>", unsafe_allow_html=True)

# ── DAU/MAU Trend by Product ───────────────────────────────
st.markdown("<div class='section-title'>📈 DAU / MAU Ratio Trend by Product</div>", unsafe_allow_html=True)

dau_mau_query = """
    WITH monthly as (
        SELECT
            product,
            DATE_TRUNC('month', date) as txn_month,
            COUNT(DISTINCT CASE WHEN dau_flag = true THEN user_id END) as dau,
            COUNT(DISTINCT CASE WHEN mau_flag = true THEN user_id END) as mau
        from vaultx_data
        GROUP BY product, DATE_TRUNC('month', date)
    )
    SELECT
        product,
        txn_month,
        ROUND(dau * 1.0 / NULLIF(mau, 0), 4) as dau_mau_ratio
    from monthly
    ORDER BY txn_month, product
"""

dau_mau_df = run_query(dau_mau_query, filtered_df)

fig_dau_mau = px.line(
    dau_mau_df,
    x='txn_month',
    y='dau_mau_ratio',
    color='product',
    markers=True,
    color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
)
fig_dau_mau.update_layout(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#F8FAFC',
    font=dict(color='#0F172A', size=13),
    legend_title='Product',
    xaxis_title='Month',
    yaxis_title='DAU / MAU Ratio',
    hovermode='x unified',
    margin=dict(t=20, b=20),
)
fig_dau_mau.update_xaxes(
    showgrid=True,
    gridcolor='#E2E8F0',
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
fig_dau_mau.update_yaxes(
    showgrid=True,
    gridcolor='#E2E8F0',
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
st.plotly_chart(fig_dau_mau, use_container_width=True)

# ── Conversion Funnel + NPS ────────────────────────────────
st.markdown("<div class='section-title'>🔽 Conversion Funnel & NPS by Product</div>", unsafe_allow_html=True)

funnel_query = """
    SELECT
        funnel_stage,
        COUNT(*) as user_count
    from vaultx_data
    GROUP BY funnel_stage
    ORDER BY
        CASE funnel_stage
            WHEN 'Install' THEN 1
            WHEN 'Registration' THEN 2
            WHEN 'First Transaction' THEN 3
            WHEN 'Repeat Transaction' THEN 4
        END
"""

funnel_df = run_query(funnel_query, filtered_df)

col1, col2 = st.columns(2)

with col1:
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_df['funnel_stage'],
        x=funnel_df['user_count'],
        textinfo='value+percent initial',
        textfont=dict(color='#0F172A', size=13),
        marker=dict(color=['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']),
    ))
    fig_funnel.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col2:
    nps_query = """
        SELECT
            product,
            ROUND(AVG(nps_score), 2) as avg_nps
        from vaultx_data
        GROUP BY product
        ORDER BY avg_nps DESC
    """
    nps_df = run_query(nps_query, filtered_df)

    fig_nps = px.bar(
        nps_df,
        x='product',
        y='avg_nps',
        color='product',
        text='avg_nps',
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
    )
    fig_nps.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        textfont=dict(color='#0F172A', size=13),
    )
    fig_nps.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        showlegend=False,
        xaxis_title='Product',
        yaxis_title='Avg NPS Score',
        yaxis=dict(range=[0, 11]),
        margin=dict(t=30, b=20),
    )
    fig_nps.update_xaxes(
        showgrid=False,
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    fig_nps.update_yaxes(
        showgrid=True,
        gridcolor='#E2E8F0',
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    st.plotly_chart(fig_nps, use_container_width=True)

# ── New vs Returning + Device Split ───────────────────────
st.markdown("<div class='section-title'>👥 New vs Returning Users & Device Split</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    new_count       = filtered_df[filtered_df['is_new_user'] == True].shape[0]
    returning_count = filtered_df[filtered_df['is_new_user'] == False].shape[0]

    fig_new = px.pie(
        names=['New Users', 'Returning Users'],
        values=[new_count, returning_count],
        hole=0.55,
        color_discrete_sequence=['#3B82F6', '#10B981'],
    )
    fig_new.update_traces(
        textfont=dict(color='#0F172A', size=13),
    )
    fig_new.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        margin=dict(t=20, b=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            font=dict(color='#0F172A'),
        ),
    )
    st.plotly_chart(fig_new, use_container_width=True)

with col2:
    device_df = filtered_df.groupby('device').size().reset_index(name='count')

    fig_device = px.pie(
        device_df,
        names='device',
        values='count',
        hole=0.55,
        color_discrete_sequence=['#F59E0B', '#EF4444', '#8B5CF6'],
    )
    fig_device.update_traces(
        textfont=dict(color='#0F172A', size=13),
    )
    fig_device.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        margin=dict(t=20, b=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            font=dict(color='#0F172A'),
        ),
    )
    st.plotly_chart(fig_device, use_container_width=True)

# ── Monthly Active Users Trend ─────────────────────────────
st.markdown("<div class='section-title'>📅 Monthly Active Users Trend</div>", unsafe_allow_html=True)

mau_trend_query = """
    SELECT
        DATE_TRUNC('month', date) as txn_month,
        COUNT(DISTINCT CASE WHEN mau_flag = true THEN user_id END) as mau,
        COUNT(DISTINCT CASE WHEN dau_flag = true THEN user_id END) as dau
    from vaultx_data
    GROUP BY DATE_TRUNC('month', date)
    ORDER BY txn_month
"""

mau_trend_df = run_query(mau_trend_query, filtered_df)

fig_mau = go.Figure()
fig_mau.add_trace(go.Scatter(
    x=mau_trend_df['txn_month'],
    y=mau_trend_df['mau'],
    name='MAU',
    line=dict(color='#3B82F6', width=2),
    fill='tozeroy',
    fillcolor='rgba(59,130,246,0.08)',
))
fig_mau.add_trace(go.Scatter(
    x=mau_trend_df['txn_month'],
    y=mau_trend_df['dau'],
    name='DAU',
    line=dict(color='#10B981', width=2),
    fill='tozeroy',
    fillcolor='rgba(16,185,129,0.08)',
))
fig_mau.update_layout(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#F8FAFC',
    font=dict(color='#0F172A', size=13),
    xaxis_title='Month',
    yaxis_title='Active Users',
    hovermode='x unified',
    margin=dict(t=20, b=20),
    legend=dict(font=dict(color='#0F172A')),
)
fig_mau.update_xaxes(
    showgrid=True,
    gridcolor='#E2E8F0',
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
fig_mau.update_yaxes(
    showgrid=True,
    gridcolor='#E2E8F0',
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
st.plotly_chart(fig_mau, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────
st.markdown("""
    <div style='text-align:center; padding:24px 0 8px;
    color:#64748B; font-size:12px;
    border-top: 1px solid #E2E8F0; margin-top:40px;'>
        Designed by Ajinkya Kadam &nbsp;|&nbsp;
        VaultX KPI Intelligence Dashboard
    </div>
""", unsafe_allow_html=True)
