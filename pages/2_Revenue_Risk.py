# ══════════════════════════════════════════════════════════
# VaultX KPI Intelligence Dashboard — Revenue & Risk View
# Author: Ajinkya Kadam
# ══════════════════════════════════════════════════════════

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, apply_filters, render_filters, kpi_card, format_number, run_query

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Revenue & Risk — VaultX",
    page_icon="💰",
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
            background: linear-gradient(135deg, #064E3B 0%, #0F172A 100%);
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
        /* Churn risk table styling */
        .risk-table {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ── Load and filter data ───────────────────────────────────
df = load_data()

# ── Page header ────────────────────────────────────────────
st.markdown("""
    <div class='page-header'>
        <div class='page-header-title'>💰 Revenue & Risk View</div>
        <div class='page-header-sub'>
            ARPU, ROAS, revenue trends and churn risk monitoring across all VaultX products and regions
        </div>
    </div>
""", unsafe_allow_html=True)

# ── Top filters ────────────────────────────────────────────
st.markdown("<div class='section-title'>🔍 Filters</div>", unsafe_allow_html=True)
products, regions, channels, date_range = render_filters(df)
filtered_df = apply_filters(df, products, regions, channels, date_range)

# ── KPI Cards ──────────────────────────────────────────────
st.markdown("<div class='section-title'>📊 Revenue KPIs</div>", unsafe_allow_html=True)

total_revenue    = filtered_df['revenue'].sum()
avg_roas         = filtered_df['roas'].mean()
avg_arpu         = filtered_df['arpu'].mean()
total_spend      = filtered_df['spend'].sum()
churn_risk_count = filtered_df[filtered_df['churn_risk'] == True].shape[0]

# ── MoM Growth calculation ─────────────────────────────────
mom_query = """
    WITH monthly as (
        SELECT
            DATE_TRUNC('month', date) as txn_month,
            SUM(revenue) as total_revenue
        from vaultx_data
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY txn_month DESC
        LIMIT 2
    )
    SELECT
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY txn_month) as prev_revenue
    from monthly
"""
mom_df = run_query(mom_query, filtered_df)
if len(mom_df) >= 2 and mom_df['prev_revenue'].iloc[0]:
    mom_growth = ((mom_df['total_revenue'].iloc[0] - mom_df['prev_revenue'].iloc[0])
                  / mom_df['prev_revenue'].iloc[0] * 100)
else:
    mom_growth = 0.0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    kpi_card("Total Revenue", format_number(total_revenue))
with col2:
    kpi_card("Avg ROAS", f"{avg_roas:.2f}x")
with col3:
    kpi_card("Avg ARPU", format_number(avg_arpu))
with col4:
    kpi_card("MoM Revenue Growth", f"{mom_growth:+.1f}%" if not __import__('math').isnan(mom_growth) else "N/A")
with col5:
    kpi_card("Churn Risk Users", f"{churn_risk_count:,}")

st.markdown("<br>", unsafe_allow_html=True)

# ── ARPU by Product + Channel ROAS ────────────────────────
st.markdown("<div class='section-title'>💎 ARPU by Product & Channel ROAS</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    arpu_query = """
        SELECT
            product,
            ROUND(AVG(arpu), 2) as avg_arpu
        from vaultx_data
        GROUP BY product
        ORDER BY avg_arpu DESC
    """
    arpu_df = run_query(arpu_query, filtered_df)

    fig_arpu = px.bar(
        arpu_df,
        x='product',
        y='avg_arpu',
        color='product',
        text='avg_arpu',
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
    )
    fig_arpu.update_traces(
        texttemplate='₹%{text:,.0f}',
        textposition='outside',
        textfont=dict(color='#0F172A', size=12),
    )
    fig_arpu.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        showlegend=False,
        xaxis_title='Product',
        yaxis_title='Avg ARPU (₹)',
        margin=dict(t=30, b=20),
        title=dict(text='Average ARPU by Product', font=dict(color='#0F172A')),
    )
    fig_arpu.update_xaxes(
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
        showgrid=False,
    )
    fig_arpu.update_yaxes(
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
        showgrid=True,
        gridcolor='#E2E8F0',
    )
    st.plotly_chart(fig_arpu, use_container_width=True)

with col2:
    roas_query = """
        SELECT
            channel,
            ROUND(AVG(roas), 2) as avg_roas
        from vaultx_data
        GROUP BY channel
        ORDER BY avg_roas DESC
    """
    roas_df = run_query(roas_query, filtered_df)

    fig_roas = px.bar(
        roas_df,
        x='channel',
        y='avg_roas',
        color='channel',
        text='avg_roas',
        color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
    )
    fig_roas.update_traces(
        texttemplate='%{text:.2f}x',
        textposition='outside',
        textfont=dict(color='#0F172A', size=12),
    )
    fig_roas.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        showlegend=False,
        xaxis_title='Channel',
        yaxis_title='Avg ROAS',
        margin=dict(t=30, b=20),
        title=dict(text='ROAS by Channel', font=dict(color='#0F172A')),
    )
    fig_roas.update_xaxes(
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
        showgrid=False,
    )
    fig_roas.update_yaxes(
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
        showgrid=True,
        gridcolor='#E2E8F0',
    )
    st.plotly_chart(fig_roas, use_container_width=True)

# ── Regional ROAS Heatmap ──────────────────────────────────
st.markdown("<div class='section-title'>🗺️ Regional ROAS Heatmap</div>", unsafe_allow_html=True)

heatmap_query = """
    SELECT
        region,
        product,
        ROUND(AVG(roas), 2) as avg_roas
    from vaultx_data
    GROUP BY region, product
    ORDER BY region, product
"""
heatmap_df = run_query(heatmap_query, filtered_df)
heatmap_pivot = heatmap_df.pivot(index='region', columns='product', values='avg_roas')

fig_heatmap = px.imshow(
    heatmap_pivot,
    color_continuous_scale='RdYlGn',
    text_auto='.2f',
    aspect='auto',
)
fig_heatmap.update_layout(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#F8FAFC',
    font=dict(color='#0F172A', size=13),
    margin=dict(t=20, b=20),
    coloraxis_colorbar=dict(
        tickfont=dict(color='#0F172A'),
        title=dict(text='ROAS', font=dict(color='#0F172A')),
    ),
)
fig_heatmap.update_xaxes(
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
fig_heatmap.update_yaxes(
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ── MoM Revenue Trend ──────────────────────────────────────
st.markdown("<div class='section-title'>📈 Month-over-Month Revenue Trend</div>", unsafe_allow_html=True)

revenue_trend_query = """
    WITH monthly_rev as (
        SELECT
            DATE_TRUNC('month', date) as txn_month,
            ROUND(SUM(revenue), 2) as total_revenue
        from vaultx_data
        GROUP BY DATE_TRUNC('month', date)
    )
    SELECT
        txn_month,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY txn_month) as prev_revenue,
        ROUND(
            (total_revenue - LAG(total_revenue) OVER (ORDER BY txn_month))
            / NULLIF(LAG(total_revenue) OVER (ORDER BY txn_month), 0) * 100
        , 2) as mom_growth_pct
    from monthly_rev
    ORDER BY txn_month
"""
revenue_trend_df = run_query(revenue_trend_query, filtered_df)

col1, col2 = st.columns(2)

with col1:
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=revenue_trend_df['txn_month'],
        y=revenue_trend_df['total_revenue'],
        name='Total Revenue',
        line=dict(color='#3B82F6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59,130,246,0.08)',
    ))
    fig_rev.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        xaxis_title='Month',
        yaxis_title='Revenue (₹)',
        margin=dict(t=20, b=20),
        title=dict(text='Monthly Revenue', font=dict(color='#0F172A')),
    )
    fig_rev.update_xaxes(
        showgrid=True, gridcolor='#E2E8F0',
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    fig_rev.update_yaxes(
        showgrid=True, gridcolor='#E2E8F0',
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

with col2:
    fig_mom = px.bar(
        revenue_trend_df.dropna(subset=['mom_growth_pct']),
        x='txn_month',
        y='mom_growth_pct',
        color='mom_growth_pct',
        color_continuous_scale=['#EF4444', '#F8FAFC', '#10B981'],
        color_continuous_midpoint=0,
    )
    fig_mom.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8FAFC',
        font=dict(color='#0F172A', size=13),
        xaxis_title='Month',
        yaxis_title='MoM Growth %',
        margin=dict(t=20, b=20),
        title=dict(text='MoM Revenue Growth %', font=dict(color='#0F172A')),
        coloraxis_showscale=False,
    )
    fig_mom.update_xaxes(
        showgrid=True, gridcolor='#E2E8F0',
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    fig_mom.update_yaxes(
        showgrid=True, gridcolor='#E2E8F0',
        tickfont=dict(color='#0F172A'),
        title_font=dict(color='#0F172A'),
    )
    st.plotly_chart(fig_mom, use_container_width=True)

# ── Revenue by Region ──────────────────────────────────────
st.markdown("<div class='section-title'>🌍 Revenue by Region</div>", unsafe_allow_html=True)

region_query = """
    SELECT
        region,
        ROUND(SUM(revenue), 2) as total_revenue,
        ROUND(AVG(roas), 2) as avg_roas,
        COUNT(*) as transactions
    from vaultx_data
    GROUP BY region
    ORDER BY total_revenue DESC
"""
region_df = run_query(region_query, filtered_df)

fig_region = px.bar(
    region_df,
    x='region',
    y='total_revenue',
    color='region',
    text='total_revenue',
    color_discrete_sequence=[
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'
    ],
)
fig_region.update_traces(
    texttemplate='₹%{text:,.0f}',
    textposition='outside',
    textfont=dict(color='#0F172A', size=12),
)
fig_region.update_layout(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#F8FAFC',
    font=dict(color='#0F172A', size=13),
    showlegend=False,
    xaxis_title='Region',
    yaxis_title='Total Revenue (₹)',
    margin=dict(t=30, b=20),
)
fig_region.update_xaxes(
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
    showgrid=False,
)
fig_region.update_yaxes(
    tickfont=dict(color='#0F172A'),
    title_font=dict(color='#0F172A'),
    showgrid=True,
    gridcolor='#E2E8F0',
)
st.plotly_chart(fig_region, use_container_width=True)

# ── Churn Risk Table ───────────────────────────────────────
st.markdown("<div class='section-title'>⚠️ High Churn Risk Customer Watch List</div>", unsafe_allow_html=True)

churn_query = """
    SELECT
        user_id as "User ID",
        product as "Product",
        region as "Region",
        channel as "Channel",
        age_group as "Age Group",
        ROUND(revenue, 2) as "Revenue (₹)",
        ROUND(arpu, 2) as "ARPU (₹)",
        nps_score as "NPS Score"
    from vaultx_data
    where churn_risk = true
    ORDER BY revenue DESC
    LIMIT 500
"""
churn_df = run_query(churn_query, filtered_df)

st.dataframe(
    churn_df,
    use_container_width=True,
    height=350,
)

# ── Footer ─────────────────────────────────────────────────
st.markdown("""
    <div style='text-align:center; padding:24px 0 8px;
    color:#64748B; font-size:12px;
    border-top: 1px solid #E2E8F0; margin-top:40px;'>
        Designed by Ajinkya Kadam &nbsp;|&nbsp;
        VaultX KPI Intelligence Dashboard
    </div>
""", unsafe_allow_html=True)
