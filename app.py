import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------
# 1. Page Configuration
# ----------------------------------------
st.set_page_config(page_title="NovaRetail Customer Intelligence", page_icon="🛍️", layout="wide")

# ----------------------------------------
# 2. Data Loading & Preprocessing
# ----------------------------------------
@st.cache_data
def load_data():
    # Load dataset (ensure the CSV is in the same directory and named 'data.csv')
    df = pd.read_csv("data.csv")
    
    # Rename 'label' to 'CustomerSegment' for clarity
    df.rename(columns={'label': 'CustomerSegment'}, inplace=True)
    
    # Convert dates
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    return df

df = load_data()

# ----------------------------------------
# 3. Sidebar Filters
# ----------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3081/3081648.png", width=100) # Placeholder logo
st.sidebar.title("NovaRetail Filters")

# Date Filter
min_date, max_date = df['TransactionDate'].min(), df['TransactionDate'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Region Filter
regions = st.sidebar.multiselect("Select Region", options=df['CustomerRegion'].unique(), default=df['CustomerRegion'].unique())

# Channel Filter
channels = st.sidebar.multiselect("Select Retail Channel", options=df['RetailChannel'].unique(), default=df['RetailChannel'].unique())

# Apply Filters
mask = (
    (df['TransactionDate'] >= pd.to_datetime(date_range[0])) & 
    (df['TransactionDate'] <= pd.to_datetime(date_range[1])) &
    (df['CustomerRegion'].isin(regions)) &
    (df['RetailChannel'].isin(channels))
)
filtered_df = df[mask]

# ----------------------------------------
# 4. Main Dashboard Header & KPIs
# ----------------------------------------
st.title("🛍️ NovaRetail Customer Intelligence Dashboard")
st.markdown("Analyze customer behavior, identify growth opportunities, and mitigate decline risks.")

# Calculate KPIs
total_revenue = filtered_df['PurchaseAmount'].sum()
total_transactions = filtered_df['TransactionID'].nunique()
avg_satisfaction = filtered_df['CustomerSatisfaction'].mean()

# "At Risk" is defined as the 'Decline' segment
risk_df = filtered_df[filtered_df['CustomerSegment'] == 'Decline']
revenue_at_risk = risk_df['PurchaseAmount'].sum()
pct_at_risk = (revenue_at_risk / total_revenue * 100) if total_revenue > 0 else 0

# Display KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Transactions", f"{total_transactions:,}")
col3.metric("Avg Satisfaction", f"{avg_satisfaction:.2f} / 5.0")
col4.metric("Revenue at Risk (Decline)", f"${revenue_at_risk:,.2f}", f"{pct_at_risk:.1f}% of total", delta_color="inverse")

st.markdown("---")

# ----------------------------------------
# 5. Visualizations
# ----------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Revenue Trend over Time")
    trend_df = filtered_df.groupby('TransactionDate')['PurchaseAmount'].sum().reset_index()
    fig_trend = px.line(trend_df, x='TransactionDate', y='PurchaseAmount', template="plotly_white")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.subheader("🎯 Revenue by Customer Segment")
    segment_df = filtered_df.groupby('CustomerSegment')['PurchaseAmount'].sum().reset_index()
    fig_segment = px.pie(segment_df, values='PurchaseAmount', names='CustomerSegment', hole=0.4, 
                         color='CustomerSegment', 
                         color_discrete_map={'Promising':'#2ca02c', 'Growth':'#1f77b4', 'Stable':'#ff7f0e', 'Decline':'#d62728'})
    st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("---")
st.subheader("💡 Growth Opportunities & Warning Signs")
col_bottom1, col_bottom2 = st.columns(2)

with col_bottom1:
    st.markdown("**Product Category Performance (Growth Opportunity)**")
    cat_df = filtered_df.groupby(['ProductCategory', 'RetailChannel'])['PurchaseAmount'].sum().reset_index()
    fig_cat = px.bar(cat_df, x='ProductCategory', y='PurchaseAmount', color='RetailChannel', barmode='group')
    st.plotly_chart(fig_cat, use_container_width=True)

with col_bottom2:
    st.markdown("**Satisfaction by Segment (Early Warning Sign)**")
    sat_df = filtered_df.groupby('CustomerSegment')['CustomerSatisfaction'].mean().reset_index()
    fig_sat = px.bar(sat_df, x='CustomerSegment', y='CustomerSatisfaction', 
                     color='CustomerSegment',
                     color_discrete_map={'Promising':'#2ca02c', 'Growth':'#1f77b4', 'Stable':'#ff7f0e', 'Decline':'#d62728'})
    fig_sat.add_hline(y=3.0, line_dash="dot", annotation_text="Danger Zone (< 3.0)", annotation_position="bottom right", line_color="red")
    st.plotly_chart(fig_sat, use_container_width=True)

# ----------------------------------------
# 6. Strategic Recommendations
# ----------------------------------------
st.markdown("### 🧠 Data-Driven Strategic Actions")
top_category = filtered_df.groupby('ProductCategory')['PurchaseAmount'].sum().idxmax() if not filtered_df.empty else "N/A"

st.info(f"""
- **Revenue Optimization (Growth):** The highest revenue is currently coming from **{top_category}**. NovaRetail should double down on cross-selling these products to the 'Promising' and 'Growth' customer segments through targeted email campaigns.
- **Retention Strategy (Risk Mitigation):** **{pct_at_risk:.1f}%** of filtered revenue comes from 'Declining' customers. Implement an immediate win-back campaign (e.g., personalized discounts) for this segment, and investigate the physical/online touchpoints where their satisfaction drops below 3.0.
- **Channel Strategy:** Evaluate the bar chart above. Shift marketing budget toward the Retail Channel that shows the highest yield in the 'Growth' segment.
""")
