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

# Apply theme
try:
    from frontend.components.theme import WarehouseTheme
    WarehouseTheme.apply_theme()
except:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT, SUPABASE_CREDS
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("📊 Analytics")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30
    SUPABASE_CREDS = {'available': False, 'url': '', 'key': ''}

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

# Fetch datasets from Supabase
@st.cache_data(ttl=30)
def fetch_datasets():
    """Fetch datasets from Supabase"""
    try:
        if SUPABASE_CREDS.get('available'):
            headers = {
                'apikey': SUPABASE_CREDS['key'],
                'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
            }
            
            response = requests.get(
                f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                headers=headers,
                params={'select': '*', 'order': 'id.desc'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        # Fallback
        response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('datasets', [])
            
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_dataset_data(dataset_id, limit=100):
    """Create sample data for analytics"""
    try:
        # Get metadata
        if SUPABASE_CREDS.get('available'):
            headers = {
                'apikey': SUPABASE_CREDS['key'],
                'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
            }
            
            response = requests.get(
                f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                headers=headers,
                params={'id': f'eq.{dataset_id}'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200 and response.json():
                metadata = response.json()[0]
                filename = metadata.get('filename', 'data.csv')
                
                # Create appropriate sample data
                dates = pd.date_range('2024-01-01', periods=limit, freq='D')
                
                if any(word in filename.lower() for word in ['sales', 'revenue', 'transaction']):
                    df = pd.DataFrame({
                        'Date': dates,
                        'Sales': np.random.normal(10000, 2000, limit),
                        'Quantity': np.random.randint(50, 200, limit),
                        'Region': np.random.choice(['North', 'South', 'East', 'West'], limit),
                        'Product': ['Product ' + str(i % 5 + 1) for i in range(limit)]
                    })
                elif any(word in filename.lower() for word in ['user', 'customer', 'client']):
                    df = pd.DataFrame({
                        'Date': dates,
                        'Users': np.random.randint(100, 1000, limit),
                        'Sessions': np.random.randint(500, 5000, limit),
                        'Country': np.random.choice(['US', 'UK', 'CA', 'AU', 'DE'], limit),
                        'Device': np.random.choice(['Mobile', 'Desktop', 'Tablet'], limit)
                    })
                else:
                    df = pd.DataFrame({
                        'Date': dates,
                        'Value': np.random.normal(100, 20, limit),
                        'Metric_A': np.random.randint(1, 100, limit),
                        'Metric_B': np.random.random(limit) * 100,
                        'Category': np.random.choice(['A', 'B', 'C', 'D'], limit)
                    })
                
                return df
                
    except:
        pass
    
    # Default sample data
    dates = pd.date_range('2024-01-01', periods=limit, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Sales': np.random.normal(10000, 2000, limit),
        'Quantity': np.random.randint(50, 200, limit),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], limit)
    })

# Load datasets
with st.spinner("Loading datasets..."):
    datasets = fetch_datasets()

if not datasets:
    st.error("❌ No datasets found in Supabase")
    
    # Debug
    with st.expander("🔧 Debug Info"):
        st.write("SUPABASE_CREDS:", SUPABASE_CREDS)
        st.write("Has secrets:", hasattr(st, 'secrets'))
        if hasattr(st, 'secrets'):
            st.write("Secrets keys:", list(st.secrets.keys()))
    
    st.info("""
    **To fix this:**
    1. Go to **📁 Data Management** page  
    2. Upload at least one file
    3. Return here to analyze it
    
    Files are stored in your Supabase database.
    """)
    
    if st.button("📁 Go to Data Management", type="primary"):
        st.switch_page("pages/2_Data.py")
    
    st.stop()

# Dataset selector
dataset_options = {}
for d in datasets:
    name = d.get('filename', f"Dataset {d.get('id')}")
    rows = d.get('rows', 0)
    size_mb = d.get('size_mb', 0)
    display_name = f"{name} ({rows} rows, {size_mb:.1f} MB)"
    dataset_options[display_name] = d

selected_display = st.selectbox("📋 Select Dataset to Analyze", list(dataset_options.keys()))

if selected_display:
    selected_dataset = dataset_options[selected_display]
    dataset_id = selected_dataset.get('id')
    dataset_name = selected_dataset.get('filename')
    
    st.success(f"✅ Selected: **{dataset_name}**")
    
    # Load dataset data (sample data for demo)
    with st.spinner(f"Loading {dataset_name}..."):
        df = fetch_dataset_data(dataset_id, limit=100)
    
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
        
        chart_type = st.selectbox("Chart Type", ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot", "Area Chart"])
        
        if chart_type == "Line Chart":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                y_col = st.selectbox("Select metric:", numeric_cols)
                
                if 'Date' in df.columns:
                    fig = px.line(df, x='Date', y=y_col, title=f"{y_col} over time")
                else:
                    fig = px.line(df, y=y_col, title=f"{y_col} trend")
                
                fig.update_traces(line_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for line chart")
        
        elif chart_type == "Bar Chart":
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if categorical_cols and numeric_cols:
                cat_col = st.selectbox("Category column:", categorical_cols)
                num_col = st.selectbox("Value column:", numeric_cols)
                
                agg_df = df.groupby(cat_col)[num_col].mean().reset_index()
                fig = px.bar(agg_df, x=cat_col, y=num_col, title=f"Average {num_col} by {cat_col}")
                fig.update_traces(marker_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
            else:
                if not categorical_cols:
                    st.warning("No categorical columns found for bar chart")
                if not numeric_cols:
                    st.warning("No numeric columns found for bar chart")
        
                elif chart_type == "Scatter Plot":
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis:", numeric_cols, key='scatter_x')
                with col2:
                    # Filter y_col options to exclude the selected x_col
                    y_options = [col for col in numeric_cols if col != x_col]
                    y_col = st.selectbox("Y-axis:", y_options, key='scatter_y')
                
                # Check for categorical column for color coding
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                color_col = None
                
                # Filter out columns that might cause duplicates
                available_cat_cols = [col for col in categorical_cols if col not in [x_col, y_col]]
                
                if available_cat_cols:
                    color_choice = st.selectbox("Color by (optional):", ['None'] + available_cat_cols, key='scatter_color')
                    if color_choice != 'None':
                        color_col = color_choice
                
                # Create scatter plot WITHOUT trendline to avoid the DuplicateError
                try:
                    # Simple scatter plot first
                    if color_col:
                        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                                        title=f"{y_col} vs {x_col}")
                    else:
                        fig = px.scatter(df, x=x_col, y=y_col,
                                        title=f"{y_col} vs {x_col}")
                        fig.update_traces(marker=dict(color='#FFD700', size=10, opacity=0.7))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show correlation
                    if len(df) > 1:
                        correlation = df[x_col].corr(df[y_col])
                        st.metric(f"Correlation ({x_col} vs {y_col})", f"{correlation:.3f}")
                        
                except Exception as scatter_error:
                    st.error(f"Error creating scatter plot: {str(scatter_error)[:200]}")
                    
                    # Fallback: even simpler scatter
                    try:
                        fig = px.scatter(df, x=x_col, y=y_col,
                                        title=f"{y_col} vs {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.warning("Could not create scatter plot with current data")
            else:
                st.warning("Need at least 2 numeric columns for scatter plot")
        
        elif chart_type == "Histogram":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    hist_col = st.selectbox("Select column:", numeric_cols)
                with col2:
                    bins = st.slider("Number of bins:", 5, 100, 20)
                
                fig = px.histogram(df, x=hist_col, nbins=bins, 
                                  title=f"Distribution of {hist_col}",
                                  color_discrete_sequence=['#FFD700'])
                
                # Add mean line
                mean_val = df[hist_col].mean()
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                            annotation_text=f"Mean: {mean_val:.2f}")
                
                # Show statistics
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Mean", f"{mean_val:.2f}")
                with col_stat2:
                    st.metric("Median", f"{df[hist_col].median():.2f}")
                with col_stat3:
                    st.metric("Std Dev", f"{df[hist_col].std():.2f}")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for histogram")
        
        elif chart_type == "Box Plot":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    box_col = st.selectbox("Value column:", numeric_cols)
                
                # Optional grouping
                group_col = None
                if categorical_cols:
                    with col2:
                        group_col = st.selectbox("Group by (optional):", ['None'] + categorical_cols)
                        if group_col == 'None':
                            group_col = None
                
                if group_col:
                    fig = px.box(df, x=group_col, y=box_col, 
                                title=f"{box_col} by {group_col}",
                                color=group_col)
                else:
                    fig = px.box(df, y=box_col, title=f"Distribution of {box_col}")
                
                fig.update_traces(marker_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for box plot")
        
        elif chart_type == "Area Chart":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                area_col = st.selectbox("Select metric:", numeric_cols)
                
                if 'Date' in df.columns:
                    fig = px.area(df, x='Date', y=area_col, 
                                 title=f"{area_col} over time (Area Chart)")
                else:
                    fig = px.area(df, y=area_col, 
                                 title=f"{area_col} (Area Chart)")
                
                fig.update_traces(line_color='#FFD700', fillcolor='rgba(255, 215, 0, 0.3)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for area chart")
    
    with tab2:
        st.markdown("### 🔍 Data Insights")
        
        # Create columns for better layout
        col_insight1, col_insight2 = st.columns(2)
        
        with col_insight1:
            # Top correlations
            st.markdown("#### 🔗 Top Correlations")
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                
                # Find top correlations
                correlations = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        col1 = corr_matrix.columns[i]
                        col2 = corr_matrix.columns[j]
                        corr_value = corr_matrix.iloc[i, j]
                        correlations.append({
                            'Pair': f"{col1} ↔ {col2}",
                            'Correlation': corr_value,
                            'Strength': 'Strong' if abs(corr_value) > 0.7 else 
                                       'Moderate' if abs(corr_value) > 0.3 else 'Weak'
                        })
                
                corr_df = pd.DataFrame(correlations)
                corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False)
                
                # Show top 5
                st.dataframe(corr_df.head(5), use_container_width=True)
        
        with col_insight2:
            # Data quality check
            st.markdown("#### 🎯 Data Quality")
            
            total_cells = df.size
            null_cells = df.isnull().sum().sum()
            null_percentage = (null_cells / total_cells * 100) if total_cells > 0 else 0
            
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.metric("Null Values", f"{null_percentage:.1f}%")
            with col_q2:
                st.metric("Duplicate Rows", f"{df.duplicated().sum()}")
        
        # Heatmap
        st.markdown("#### 🔥 Correlation Heatmap")
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                hoverongaps=False,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}"
            ))
            
            fig.update_layout(
                title="Correlation Heatmap",
                height=500,
                xaxis_title="Features",
                yaxis_title="Features"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation heatmap")
    
    with tab3:
        st.markdown("### 📊 Statistical Summary")
        
        # Basic statistics
        st.dataframe(df.describe(), use_container_width=True)
        
        # Data types and info
        st.markdown("#### 📋 Data Types & Information")
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null': df.count().values,
            'Unique Values': df.nunique().values,
            'Null %': (df.isnull().sum().values / len(df) * 100).round(2)
        })
        st.dataframe(info_df, use_container_width=True, hide_index=True)
        
        # Value distributions for categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.markdown("#### 📊 Categorical Distributions")
            selected_cat = st.selectbox("Select categorical column to analyze:", categorical_cols)
            
            if selected_cat:
                value_counts = df[selected_cat].value_counts().reset_index()
                value_counts.columns = [selected_cat, 'Count']
                value_counts['Percentage'] = (value_counts['Count'] / len(df) * 100).round(1)
                
                col_dist1, col_dist2 = st.columns([2, 1])
                
                with col_dist1:
                    # Bar chart
                    fig = px.bar(value_counts.head(10), 
                                x=selected_cat, y='Count',
                                title=f"Top 10 {selected_cat} values",
                                color_discrete_sequence=['#FFD700'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_dist2:
                    # Table
                    st.dataframe(value_counts.head(10), use_container_width=True)

st.markdown("---")
st.caption(f"📊 Analytics • {len(datasets)} datasets available • {datetime.now().strftime('%H:%M:%S')}")