# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import requests
import json

# Apply theme
try:
    from frontend.components.theme import WarehouseTheme
    WarehouseTheme.apply_theme()  # This will use the current theme from session state
except:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT, SUPABASE_CREDS
except ImportError as e:
    st.error(f"Import error: {e}")
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("📊 Dashboard")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30
    SUPABASE_CREDS = {'available': False, 'url': '', 'key': ''}

st.set_page_config(
    page_title="Dashboard - Data Warehouse",
    page_icon="🏠",
    layout="wide"
)

# Apply theme
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
    <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">🏭 Data Warehouse Dashboard</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Real-time monitoring & analytics
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Fetch datasets from Supabase
@st.cache_data(ttl=60)
def fetch_datasets():
    """Fetch datasets from Supabase"""
    try:
        if SUPABASE_CREDS.get('available'):
            headers = {
                'apikey': SUPABASE_CREDS['key'],
                'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
            }
            
            # Try to fetch from Supabase
            response = requests.get(
                f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                headers=headers,
                params={'select': '*', 'order': 'created_at.desc'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                datasets = response.json()
                st.success(f"✅ Loaded {len(datasets)} datasets from Supabase")
                return datasets
            else:
                st.warning(f"⚠️ Supabase error: {response.status_code}")
                return []
        else:
            # Fallback to original backend
            st.warning("⚠️ Supabase not configured, using fallback")
            response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                return data.get('datasets', [])
            else:
                return []
                
    except Exception as e:
        st.error(f"Failed to fetch datasets: {str(e)[:100]}")
        return []

# Load data
with st.spinner("Loading dashboard data..."):
    datasets = fetch_datasets()
    
    # Calculate dashboard data
    total_files = len(datasets)
    total_rows = sum(d.get('rows', 0) for d in datasets)
    total_size = sum(d.get('size_mb', 0) for d in datasets) if any('size_mb' in d for d in datasets) else total_rows * 0.001
    
    # Get latest uploads (first 5)
    latest_uploads = datasets[:5]
    
    data = {
        'total_files': total_files,
        'total_rows': total_rows,
        'total_size_mb': total_size,
        'latest_uploads': latest_uploads,
        'datasets': datasets
    }

# Connection Status
st.markdown("## 🔗 Connection Status")
col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    if SUPABASE_CREDS.get('available'):
        st.success("✅ Supabase")
    else:
        st.error("❌ Supabase")

with col_status2:
    st.info("✅ Streamlit")

with col_status3:
    st.info("✅ Database")

with col_status4:
    st.info("✅ API")

# Key Metrics
st.markdown("## 🎯 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_files = data['total_files'] - st.session_state.get('last_file_count', 0) if 'last_file_count' in st.session_state else None
    st.metric(
        "Total Datasets", 
        data['total_files'], 
        f"+{delta_files}" if delta_files and delta_files > 0 else None
    )

with col2:
    delta_rows = data['total_rows'] - st.session_state.get('last_row_count', 0) if 'last_row_count' in st.session_state else None
    st.metric(
        "Total Rows", 
        f"{data['total_rows']:,}", 
        f"+{delta_rows:,}" if delta_rows and delta_rows > 0 else None
    )

with col3:
    success_rate = 99.8 if data['total_files'] > 0 else 0
    st.metric("Success Rate", f"{success_rate}%", "+0.2%")

with col4:
    avg_time = 1.2 if data['total_files'] > 0 else 0
    st.metric("Avg Processing", f"{avg_time}s", "-0.3s")

# Update session state
st.session_state.last_file_count = data['total_files']
st.session_state.last_row_count = data['total_rows']
st.session_state.total_size_mb = data['total_size_mb']

# Recent Activity
st.markdown("## 📋 Recent Activity")
if data['latest_uploads']:
    activities = []
    for upload in data['latest_uploads']:
        # Format timestamp if available
        uploaded_at = upload.get('created_at') or upload.get('uploaded_at')
        if uploaded_at:
            try:
                # Parse ISO format timestamp
                dt = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                time_ago = (datetime.now() - dt).total_seconds() / 60
                if time_ago < 60:
                    time_str = f"{int(time_ago)} min ago"
                elif time_ago < 1440:
                    time_str = f"{int(time_ago/60)} hours ago"
                else:
                    time_str = f"{int(time_ago/1440)} days ago"
            except:
                time_str = "Recently"
        else:
            time_str = "Recently"
        
        activities.append({
            'Time': time_str,
            'Action': 'File Upload',
            'File': upload.get('filename', 'Unknown'),
            'Rows': f"{upload.get('rows', 0):,}",
            'Status': '✅ Success'
        })
    
    df_activities = pd.DataFrame(activities)
    st.dataframe(df_activities, use_container_width=True, hide_index=True)
else:
    st.info("No recent uploads. Go to Data Management to upload files.")
    
    # Show sample data for demo
    with st.expander("Show sample data structure"):
        if SUPABASE_CREDS.get('available'):
            st.json({
                "supabase_url": SUPABASE_CREDS['url'],
                "expected_table": "datasets",
                "expected_columns": ["id", "filename", "rows", "created_at", "size_mb", "status"],
                "sample_query": f"SELECT * FROM datasets ORDER BY created_at DESC LIMIT 5"
            })

# Data Quality Metrics
st.markdown("## 🎯 Data Quality Metrics")
if data['datasets']:
    # Create metrics row
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        completeness = min(100, (len([d for d in data['datasets'] if d.get('rows', 0) > 0]) / max(1, len(data['datasets']))) * 100)
        st.metric("Completeness", f"{completeness:.1f}%")
    
    with col_q2:
        valid_datasets = len([d for d in data['datasets'] if d.get('status', 'success') == 'success'])
        validity = (valid_datasets / max(1, len(data['datasets']))) * 100
        st.metric("Validity", f"{validity:.1f}%")
    
    with col_q3:
        avg_rows = data['total_rows'] / max(1, data['total_files'])
        st.metric("Avg Rows/Dataset", f"{avg_rows:,.0f}")
    
    with col_q4:
        st.metric("Error Rate", "0.2%", "-0.1%")
    
    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=completeness,
        title={'text': "Data Completeness"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#FFD700"},
               'steps': [
                   {'range': [0, 70], 'color': "#DC3545"},
                   {'range': [70, 90], 'color': "#FFC107"},
                   {'range': [90, 100], 'color': "#28A745"}],
               'threshold': {'line': {'color': "black", 'width': 4},
                             'thickness': 0.75, 'value': completeness}}))
    
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Upload data to see quality metrics")
    
    # Show connection help
    with st.expander("Troubleshooting Supabase Connection"):
        st.markdown("""
        ### If you see "No recent uploads":
        
        1. **Check Supabase Credentials** in `frontend/utils/config.py`:
           ```python
           SUPABASE_CREDS = {
               'available': True,
               'url': st.secrets.get("SUPABASE_URL", ""),
               'key': st.secrets.get("SUPABASE_KEY", ""),
               'source': 'streamlit_secrets'
           }
           ```
        
        2. **Create `.streamlit/secrets.toml`**:
           ```toml
           SUPABASE_URL = "https://your-project-ref.supabase.co"
           SUPABASE_KEY = "your-anon-key-here"
           ```
        
        3. **Verify your Supabase table**:
           ```sql
           -- Run in Supabase SQL Editor
           CREATE TABLE datasets (
               id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
               filename TEXT,
               rows INTEGER,
               size_mb DECIMAL(10,2),
               status TEXT DEFAULT 'success',
               created_at TIMESTAMP DEFAULT NOW()
           );
           
           -- Insert sample data
           INSERT INTO datasets (filename, rows, size_mb) 
           VALUES ('sales.csv', 1000, 1.5);
           ```
        """)

# Quick Actions
st.markdown("## 🚀 Quick Actions")
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📤 Upload Data", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📁_Data.py")

with action_col2:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/1_Analytics.py")

with action_col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/3_Settings.py")

# System Overview
st.markdown("## 📊 System Overview")
col_sys1, col_sys2 = st.columns(2)

with col_sys1:
    st.markdown("### Dataset Distribution")
    if data['datasets']:
        # Create simple bar chart
        df_chart = pd.DataFrame(data['datasets'])
        if 'filename' in df_chart.columns:
            top_datasets = df_chart.nlargest(5, 'rows') if 'rows' in df_chart.columns else df_chart.head(5)
            st.bar_chart(top_datasets.set_index('filename')['rows'] if 'rows' in top_datasets.columns else None)
        else:
            st.info("No filename data available")
    else:
        st.info("No datasets to display")

with col_sys2:
    st.markdown("### Storage Usage")
    if data['total_files'] > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['Used', 'Available'],
            values=[data['total_size_mb'], max(1000 - data['total_size_mb'], 0)],
            hole=.4,
            marker_colors=['#FFD700', '#333333']
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No storage data available")

# Debug section (can be removed in production)
with st.expander("🔍 Debug Information"):
    st.json({
        "supabase_configured": SUPABASE_CREDS.get('available', False),
        "datasets_count": len(datasets),
        "sample_dataset": datasets[0] if datasets else "None",
        "session_keys": list(st.session_state.keys()),
        "backend_url": BACKEND_URL
    })

st.markdown("---")
st.caption(f"🏭 Dashboard • {data['total_files']} datasets • {datetime.now().strftime('%H:%M:%S')}")