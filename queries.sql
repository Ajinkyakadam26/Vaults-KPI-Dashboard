-- ══════════════════════════════════════════════════════════
-- VaultX KPI Intelligence Dashboard — SQL Queries
-- Author: Ajinkya Kadam
-- Tool: DuckDB
-- Data: vaultx_data.csv (1,000,000 rows)
-- ══════════════════════════════════════════════════════════


-- ── Query 1: Revenue by Product
-- Shows average and total revenue per product
-- Used in: Revenue & Risk View — Revenue by Product chart

SELECT
    product,
    ROUND(AVG(revenue), 2) as avg_revenue,
    ROUND(SUM(revenue), 2) as total_revenue,
    COUNT(*) as total_transactions
from vaultx_data
GROUP BY product
ORDER BY avg_revenue DESC


-- ── Query 2: ROAS by Channel
-- Compares return on ad spend across all 4 channels
-- Used in: Revenue & Risk View — Channel ROAS chart

SELECT
    channel,
    ROUND(AVG(roas), 2) as avg_roas,
    ROUND(SUM(revenue), 2) as total_revenue,
    ROUND(SUM(spend), 2) as total_spend
from vaultx_data
GROUP BY channel
ORDER BY avg_roas DESC


-- ── Query 3: DAU/MAU Ratio by Product and Month
-- Tracks engagement stickiness per product over time
-- Used in: Product & Growth View — DAU/MAU trend

WITH monthly_stats as (
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
    dau,
    mau,
    ROUND(dau * 1.0 / NULLIF(mau, 0), 4) as dau_mau_ratio
from monthly_stats
ORDER BY txn_month, product


-- ── Query 4: Monthly Revenue Trend with MoM Growth
-- Tracks revenue growth month over month using LAG window function
-- Used in: Revenue & Risk View — MoM Revenue trend

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
    LAG(total_revenue) OVER (ORDER BY txn_month) as prev_month_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY txn_month))
        / NULLIF(LAG(total_revenue) OVER (ORDER BY txn_month), 0) * 100
    , 2) as mom_growth_pct
from monthly_rev
ORDER BY txn_month


-- ── Query 5: Funnel Drop-off Analysis
-- Measures how many users drop at each funnel stage
-- Used in: Product & Growth View — Conversion Funnel

SELECT
    funnel_stage,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as stage_pct
from vaultx_data
GROUP BY funnel_stage
ORDER BY
    CASE funnel_stage
        WHEN 'Install' THEN 1
        WHEN 'Registration' THEN 2
        WHEN 'First Transaction' THEN 3
        WHEN 'Repeat Transaction' THEN 4
    END


-- ── Query 6: ARPU by Product and Region
-- Double group by to find which product + region combo gives best ARPU
-- Used in: Revenue & Risk View — Regional ROAS heatmap

SELECT
    product,
    region,
    ROUND(AVG(arpu), 2) as avg_arpu,
    ROUND(SUM(revenue), 2) as total_revenue,
    COUNT(DISTINCT user_id) as unique_users
from vaultx_data
GROUP BY product, region
ORDER BY avg_arpu DESC


-- ── Query 7: NPS Score Distribution by Product
-- Segments users into Promoters, Passives, Detractors
-- Used in: Product & Growth View — NPS by Product

SELECT
    product,
    ROUND(AVG(nps_score), 2) as avg_nps,
    COUNT(CASE WHEN nps_score >= 9 THEN 1 END) as promoters,
    COUNT(CASE WHEN nps_score BETWEEN 7 AND 8 THEN 1 END) as passives,
    COUNT(CASE WHEN nps_score <= 6 THEN 1 END) as detractors,
    ROUND(
        (COUNT(CASE WHEN nps_score >= 9 THEN 1 END) * 100.0
        - COUNT(CASE WHEN nps_score <= 6 THEN 1 END) * 100.0)
        / COUNT(*), 2
    ) as nps_final_score
from vaultx_data
GROUP BY product
ORDER BY avg_nps DESC


-- ── Query 8: Churn Risk Users
-- Filters high risk users sorted by revenue descending
-- Used in: Revenue & Risk View — Churn Risk table

SELECT
    user_id,
    product,
    region,
    channel,
    age_group,
    ROUND(revenue, 2) as revenue,
    ROUND(arpu, 2) as arpu,
    nps_score,
    churn_risk
from vaultx_data
where churn_risk = true
ORDER BY revenue DESC
LIMIT 500
