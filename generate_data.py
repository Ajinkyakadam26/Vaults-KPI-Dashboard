import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

# ── Seed ──────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Constants ─────────────────────────────────────────────
N_ROWS = 1_000_000

PRODUCTS   = ['Payments', 'Lending', 'Insurance', 'Investments']
REGIONS    = ['North', 'South', 'East', 'West', 'International']
CHANNELS   = ['Organic', 'Paid', 'Referral', 'App Store']
DEVICES    = ['Mobile', 'Desktop', 'Tablet']
AGE_GROUPS = ['18-25', '26-35', '36-45', '45+']

START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2026, 6, 30)
DATE_RANGE = (END_DATE - START_DATE).days

# ── Revenue profiles (Investments >> Lending >> Insurance >> Payments)
REVENUE_PROFILES = {
    'Payments':    {'mean': 150,   'std': 200},
    'Lending':     {'mean': 2500,  'std': 3000},
    'Insurance':   {'mean': 800,   'std': 600},
    'Investments': {'mean': 8000,  'std': 7000},
}

# ── Spend profiles (Paid >> App Store >> Referral >> Organic)
SPEND_PROFILES = {
    'Organic':   {'mean': 10,  'std': 15},
    'Paid':      {'mean': 500, 'std': 400},
    'Referral':  {'mean': 80,  'std': 60},
    'App Store': {'mean': 250, 'std': 200},
}

# ── ROAS profiles (Organic best, Paid worst)
ROAS_PROFILES = {
    'Organic':   {'mean': 6.5, 'std': 2.0},
    'Referral':  {'mean': 4.2, 'std': 1.5},
    'App Store': {'mean': 2.8, 'std': 1.2},
    'Paid':      {'mean': 1.4, 'std': 0.8},
}

# ── NPS profiles (Investments best, Insurance worst)
NPS_PROFILES = {
    'Investments': {'mean': 8.5, 'std': 1.0},
    'Payments':    {'mean': 7.2, 'std': 1.5},
    'Lending':     {'mean': 5.8, 'std': 2.0},
    'Insurance':   {'mean': 4.5, 'std': 2.5},
}

# ── DAU probability per product (Payments most active, Insurance least)
DAU_PROBS = {
    'Payments':    0.75,
    'Investments': 0.50,
    'Lending':     0.28,
    'Insurance':   0.10,
}

# ── Regional revenue multipliers (North best, International worst)
REGION_MULTIPLIERS = {
    'North':         1.35,
    'South':         1.20,
    'East':          1.00,
    'West':          0.85,
    'International': 0.60,
}

# ── Churn risk per channel (Paid highest, Organic lowest)
CHURN_RISK_PROBS = {
    'Paid':      0.35,
    'App Store': 0.25,
    'Referral':  0.15,
    'Organic':   0.08,
}

# ── Seasonal multipliers per month (peaks in Oct-Dec)
SEASONAL = {
    1: 0.75, 2: 0.78, 3: 0.85,
    4: 0.90, 5: 0.92, 6: 0.95,
    7: 0.97, 8: 1.00, 9: 1.05,
    10: 1.15, 11: 1.25, 12: 1.35
}

print("⏳ Generating 1,000,000 rows of VaultX data...")

# ── Base columns ───────────────────────────────────────────
transaction_ids = [
    'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    for _ in range(N_ROWS)
]

user_ids = ['USR' + str(random.randint(10000, 999999)) for _ in range(N_ROWS)]

dates = [START_DATE + timedelta(days=random.randint(0, DATE_RANGE)) for _ in range(N_ROWS)]

products = np.random.choice(PRODUCTS, N_ROWS, p=[0.40, 0.25, 0.20, 0.15])
regions  = np.random.choice(REGIONS,  N_ROWS, p=[0.25, 0.22, 0.20, 0.18, 0.15])
channels = np.random.choice(CHANNELS, N_ROWS, p=[0.35, 0.30, 0.20, 0.15])
devices  = np.random.choice(DEVICES,  N_ROWS, p=[0.65, 0.25, 0.10])
age_groups = np.random.choice(AGE_GROUPS, N_ROWS, p=[0.28, 0.35, 0.22, 0.15])

# ── Revenue with regional multiplier + seasonality ─────────
revenue = np.array([
    max(10, np.random.normal(
        REVENUE_PROFILES[p]['mean'], REVENUE_PROFILES[p]['std']
    ) * REGION_MULTIPLIERS[r] * SEASONAL[d.month])
    for p, r, d in zip(products, regions, dates)
]).round(2)

# ── Spend ──────────────────────────────────────────────────
spend = np.array([
    max(1, np.random.normal(
        SPEND_PROFILES[c]['mean'], SPEND_PROFILES[c]['std']
    ))
    for c in channels
]).round(2)

# ── ROAS ───────────────────────────────────────────────────
roas = np.array([
    max(0.1, np.random.normal(
        ROAS_PROFILES[c]['mean'], ROAS_PROFILES[c]['std']
    ))
    for c in channels
]).round(2)

# ── NPS ────────────────────────────────────────────────────
nps_scores = np.array([
    int(np.clip(np.random.normal(
        NPS_PROFILES[p]['mean'], NPS_PROFILES[p]['std']
    ), 0, 10))
    for p in products
])

# ── DAU / MAU flags ────────────────────────────────────────
dau_flags = np.array([
    np.random.random() < DAU_PROBS[p]
    for p in products
])

mau_flags = np.array([
    dau or (np.random.random() < min(DAU_PROBS[p] + 0.25, 1.0))
    for p, dau in zip(products, dau_flags)
])

# ── ARPU ───────────────────────────────────────────────────
arpu = (revenue * np.random.uniform(0.8, 1.2, N_ROWS)).round(2)

# ── New user flag (newer dates = more new users) ───────────
is_new_user = np.array([
    np.random.random() < (0.45 - (d.year - 2024) * 0.08)
    for d in dates
])

# ── Repeat transaction (inverse of new user + product factor)
repeat_probs = {
    'Payments':    0.72,
    'Investments': 0.55,
    'Lending':     0.38,
    'Insurance':   0.20,
}
is_repeat_transaction = np.array([
    (not new) and (np.random.random() < repeat_probs[p])
    for new, p in zip(is_new_user, products)
])

# ── Session duration (Mobile shorter, Desktop longer) ──────
session_base = {'Mobile': 180, 'Desktop': 420, 'Tablet': 300}
session_duration = np.array([
    max(10, int(np.random.normal(session_base[d], session_base[d] * 0.5)))
    for d in devices
])

# ── Churn risk ─────────────────────────────────────────────
churn_risk = np.array([
    np.random.random() < CHURN_RISK_PROBS[c]
    for c in channels
])

# ── Funnel stage ───────────────────────────────────────────
funnel_probs = [0.30, 0.28, 0.22, 0.20]
funnel_stages = np.random.choice(
    ['Install', 'Registration', 'First Transaction', 'Repeat Transaction'],
    N_ROWS, p=funnel_probs
)

# ── Build DataFrame ────────────────────────────────────────
df = pd.DataFrame({
    'transaction_id':       transaction_ids,
    'user_id':              user_ids,
    'date':                 dates,
    'product':              products,
    'region':               regions,
    'channel':              channels,
    'device':               devices,
    'age_group':            age_groups,
    'revenue':              revenue,
    'spend':                spend,
    'roas':                 roas,
    'arpu':                 arpu,
    'nps_score':            nps_scores,
    'dau_flag':             dau_flags,
    'mau_flag':             mau_flags,
    'is_new_user':          is_new_user,
    'is_repeat_transaction': is_repeat_transaction,
    'session_duration':     session_duration,
    'churn_risk':           churn_risk,
    'funnel_stage':         funnel_stages,
})

# ── Save ───────────────────────────────────────────────────
df.to_csv('vaultx_data.csv', index=False)

print("✅ Done! vaultx_data.csv created successfully")
print(f"   Rows    : {len(df):,}")
print(f"   Columns : {len(df.columns)}")
print(f"   Date range: {df['date'].min()} → {df['date'].max()}")
print(f"\n📊 Revenue by Product:")
print(df.groupby('product')['revenue'].mean().round(0).sort_values(ascending=False))
print(f"\n📊 ROAS by Channel:")
print(df.groupby('channel')['roas'].mean().round(2).sort_values(ascending=False))
print(f"\n📊 Avg NPS by Product:")
print(df.groupby('product')['nps_score'].mean().round(1).sort_values(ascending=False))
