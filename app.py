import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide", page_title="NovaRetail Data Dashboard")
st.title("NovaRetail Data Dashboard")
st.subheader("Sales Analysis by Region and Demographics")

# STEP 3 — Load Data
@st.cache_data
def load_data():
    file_path = "NR_dataset.xlsx"
    try:
        # Loading Excel as per strict data handling rules
        df = pd.read_excel(file_path)
        
        # Normalize column names: strip whitespace, lowercase, replace spaces with underscores
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        
        return df, None
    except FileNotFoundError:
        return None, "Dataset file not found in repository."
    except Exception as e:
        return None, f"Error loading data: {e}"

df_raw, error_msg = load_data()

if error_msg:
    st.error(error_msg)
else:
    # Required logical fields based on Section C and dataset structure
    # Based on normalization, 'CustomerRegion' becomes 'customerregion', etc.
    required_fields = ['customerregion', 'customergender', 'productcategory', 'purchaseamount']
