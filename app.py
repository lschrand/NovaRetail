import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide", page_title="Provisional Natality Data Dashboard")

# Header section
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
@st.cache_data
def load_data():
    # Strict requirement: Load this specific CSV filename
    file_path = "Provisional_Natality_2025_CDC.csv"
    try:
        df = pd.read_csv(file_path)
        
        # Normalize column names: strip whitespace, lowercase, spaces to underscores
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        
        return df, None
    except FileNotFoundError:
        return None, "Dataset file not found in repository."
    except Exception as e:
        return None, f"Error loading data: {e}"

df_raw, error_msg = load_data()

# Error handling for file missing
if error_msg:
    st.error(error_msg)
else:
    # Required logical fields based on Section C, Step 6/7
    # Note: Mapping logical "State" to 'state_of_residence' and "Births" to 'births'
    required_fields = ['state_of_residence', 'gender', 'births']
    
    # Validate required logical fields
    missing_fields = [field for field in required_fields if field not in df_raw.columns]
    
    if missing_fields:
        st.error(f"Required logical fields missing: {', '.join(missing_fields)}")
        st.write("Actual columns found in CSV:")
        st.write(df_raw.columns.tolist())
    else:
        # STEP 4 — Sidebar Filters
        st.sidebar.header("Data Filters")
        
        # State Filter
        all_states = sorted(df_raw['state_of_residence'].unique().tolist())
        sel_states = st.sidebar.multiselect(
            "Select State of Residence:", 
            options=["All"] + all_states, 
            default=["All"]
        )
        
        # Gender Filter
        all_genders = sorted(df_raw['gender'].unique().tolist())
        sel_genders = st.sidebar.multiselect(
            "Select Gender:", 
            options=["All"] + all_genders, 
            default=["All"]
        )

        # STEP 5 — Filtering Logic
        df_filtered = df_raw.copy()

        if "All" not in sel_states:
            df_filtered = df_filtered[df_filtered['state_of_residence'].isin(sel_states)]
        
        if "All" not in sel_genders:
            df_filtered = df_filtered[df_filtered['gender'].isin(sel_genders)]

        # STEP 9 — Edge Case: Empty Result
        if df_filtered.empty:
            st.warning("No data matches the selected filter criteria.")
        else:
            # STEP 6 — Aggregation
            # Grouping by state and gender as per requirements
            df_agg = df_filtered.groupby(['state_of_residence', 'gender'], as_index=False)['births'].sum()

            # STEP 7 — Plot
            fig = px.bar(
                df_agg,
                x='state_of_residence',
                y='births',
                color='gender',
                barmode='group',
                title="Birth Volume by State and Gender",
                labels={
                    'state_of_residence': 'State of Residence',
                    'births': 'Number of Births',
                    'gender': 'Gender'
                },
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            # STEP 8 — Show Filtered Table
            st.write("### Data Preview")
            # Cleaning display by removing index
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)

# End of app.py
