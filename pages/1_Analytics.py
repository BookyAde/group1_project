# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import requests
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("📊 Analytics")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30

st.set_page_config(
    page_title="Analytics - Data Warehouse",
    page_icon="📊",
    layout="wide"
)

if 'user_email' not in st.session_state:
    st.warning("⚠️ Please login first")
    st.stop()

try:
    WarehouseTheme.apply_global_styles()
except:
    pass

# Render sidebar
try:
    render_sidebar()
except Exception as e:
    st.sidebar.error(f"Sidebar error: {e}")

# Header
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">📊 Advanced Analytics</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Interactive data visualization and insights
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Fetch datasets from backend
@st.cache_data(ttl=30)
def fetch_datasets():
    """Fetch datasets from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('datasets', [])
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_dataset_data(upload_id, limit=100):
    """Fetch specific dataset data"""
    try:
        response = requests.get(f"{BACKEND_URL}/data/file/{upload_id}?limit={limit}", timeout=TIMEOUT)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

# Load datasets
with st.spinner("Loading datasets..."):
    datasets = fetch_datasets()

if not datasets:
    st.error("❌ No datasets found in backend")
    st.info("""
    **Please:**
    1. Go to **📁 Data Management** page
    2. Upload your datasets (CSV/Excel files)
    3. Return here to analyze them
    """)
    
    if st.button("📁 Go to Data Management", type="primary"):
        st.switch_page("pages/2_📁_Data.py")
    
    st.stop()

# Dataset selector
dataset_options = {f"{d.get('filename')} ({d.get('rows')} rows)": d for d in datasets}
selected_display = st.selectbox("📋 Select Dataset to Analyze", list(dataset_options.keys()))

if selected_display:
    selected_dataset = dataset_options[selected_display]
    dataset_id = selected_dataset.get('id')
    dataset_name = selected_dataset.get('filename')
    
    st.success(f"✅ Selected: **{dataset_name}** ({selected_dataset.get('rows')} rows)")
    
    # Load dataset data
    with st.spinner(f"Loading {dataset_name}..."):
        df = fetch_dataset_data(dataset_id, limit=100)
    
    if df.empty:
        st.error(f"Could not load data for {dataset_name}")
        st.info("The dataset might be empty or there's a connection issue.")
        
        # Create sample data for demo
        if st.checkbox("Load sample data for demonstration"):
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            df = pd.DataFrame({
                'Date': dates,
                'Sales': np.random.normal(10000, 2000, 100),
                'Quantity': np.random.randint(50, 200, 100),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
            })
        else:
            st.stop()
    
    # Data preview
    with st.expander("👁️ Data Preview", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)
        
        # Data info
        st.markdown("#### Data Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            st.metric("Numeric Columns", len(numeric_cols))
    
    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["📈 Charts", "🔍 Insights", "📊 Statistics"])
    
    with tab1:
        st.markdown("### 📈 Interactive Visualization")
        
        chart_type = st.selectbox("Chart Type", ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram"])
        
        if chart_type == "Line Chart":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                y_col = st.selectbox("Select metric:", numeric_cols)
                
                # Check for date column
                date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'time', 'day'])]
                if date_cols:
                    x_col = st.selectbox("X-axis (date):", date_cols)
                    fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over time")
                else:
                    fig = px.line(df, y=y_col, title=f"{y_col} trend")
                
                fig.update_traces(line_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Bar Chart":
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if categorical_cols and numeric_cols:
                cat_col = st.selectbox("Category column:", categorical_cols)
                num_col = st.selectbox("Value column:", numeric_cols)
                
                # Aggregate
                agg_df = df.groupby(cat_col)[num_col].mean().reset_index()
                fig = px.bar(agg_df, x=cat_col, y=num_col, title=f"Average {num_col} by {cat_col}")
                fig.update_traces(marker_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🔍 Data Insights")
        
        # Correlation matrix for numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0
            ))
            
            fig.update_layout(title="Correlation Heatmap", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 Statistical Summary")
        
        # Show statistics
        st.dataframe(df.describe(), use_container_width=True)
        
        # Data types
        st.markdown("#### Data Types")
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null': df.count().values,
            'Unique': df.nunique().values
        })
        st.dataframe(info_df, use_container_width=True)
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"{dataset_name.split('.')[0]}_analytics.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = df.head(50).to_json(orient='records', indent=2)
        st.download_button(
            label="📊 Download as JSON",
            data=json_data,
            file_name=f"{dataset_name.split('.')[0]}_analytics.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")
st.caption(f"📊 Analytics • {len(datasets)} datasets available • {datetime.now().strftime('%H:%M:%S')}")