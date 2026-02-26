import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="NovaRetail Data Dashboard")
st.title("NovaRetail Data Dashboard")
st.subheader("Sales Analysis by Region and Demographics")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("NR_dataset.xlsx")
        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
        return df, None
    except FileNotFoundError:
        return None, "Dataset file not found in repository."
    except Exception as e:
        return None, f"An error occurred loading the data: {e}"

df_raw, error_message = load_data()

if error_message:
    st.error(error_message)
else:
    required_fields = ['customer_region', 'customer_gender', 'product_category', 'purchase_amount']
    missing_fields = [field for field in required_fields if field not in df_raw.columns]
    
    if missing_fields:
        st.error(f"Missing required logical fields: {', '.join(missing_fields)}")
        st.write(df_raw.columns.tolist())
    else:
        df_raw['purchase_amount'] = pd.to_numeric(df_raw['purchase_amount'], errors='coerce')
        df_raw = df_raw.dropna(subset=['purchase_amount'])
        
        st.sidebar.header("Filters")
        
        region_options = ["All"] + sorted(df_raw['customer_region'].astype(str).unique().tolist())
        gender_options = ["All"] + sorted(df_raw['customer_gender'].astype(str).unique().tolist())
        category_options = ["All"] + sorted(df_raw['product_category'].astype(str).unique().tolist())
        
        selected_regions = st.sidebar.multiselect("Select Region", options=region_options, default=["All"])
        selected_genders = st.sidebar.multiselect("Select Gender", options=gender_options, default=["All"])
        selected_categories = st.sidebar.multiselect("Select Product Category", options=category_options, default=["All"])
        
        df_filtered = df_raw.copy()
        
        if "All" not in selected_regions:
            df_filtered = df_filtered[df_filtered['customer_region'].isin(selected_regions)]
            
        if "All" not in selected_genders:
            df_filtered = df_filtered[df_filtered['customer_gender'].isin(selected_genders)]
            
        if "All" not in selected_categories:
            df_filtered = df_filtered[df_filtered['product_category'].isin(selected_categories)]
            
        if df_filtered.empty:
            st.warning("No data matches the selected filters.")
        else:
            df_agg = df_filtered.groupby(['customer_region', 'customer_gender'], as_index=False)['purchase_amount'].sum()
            df_agg = df_agg.sort_values('customer_region')
            
            fig = px.bar(
                df_agg,
                x='customer_region',
                y='purchase_amount',
                color='customer_gender',
                title="Total Sales by Region and Gender",
                template="plotly_white",
                labels={
                    'customer_region': 'Customer Region',
                    'purchase_amount': 'Purchase Amount',
                    'customer_gender': 'Gender'
                }
            )
            fig.update_layout(legend_title_text="Gender")
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
