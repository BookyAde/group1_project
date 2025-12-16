# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import requests
from io import BytesIO

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
    from frontend.utils.config import BACKEND_URL, TIMEOUT, SUPABASE_CREDS  # Added SUPABASE_CREDS
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("📁 Data Management")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30
    SUPABASE_CREDS = {'available': False, 'url': '', 'key': ''}  # Fallback

st.set_page_config(
    page_title="Data Management - Data Warehouse",
    page_icon="📁",
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
    <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">📁 Data Management</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Upload, manage, and organize your datasets
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Fetch current datasets from Supabase
@st.cache_data(ttl=30)
def fetch_datasets():
    """Fetch datasets from Supabase or fallback"""
    try:
        # Use Supabase if available
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
                st.error(f"Supabase error {response.status_code}")
                return []
                
        # Fallback to original backend
        response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('datasets', [])
            
    except Exception as e:
        st.error(f"Fetch error: {str(e)[:100]}")
        
    return []

# Upload section
st.markdown("## 📤 Upload to Supabase")

upload_tab1, upload_tab2 = st.tabs(["File Upload", "Quick Templates"])

with upload_tab1:
    uploaded_files = st.file_uploader(
        "Choose files (CSV, Excel)",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        help="Max 10 MB per file"
    )
    
    if uploaded_files:
        st.markdown(f"#### Selected Files ({len(uploaded_files)})")
        
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(file.name)
            with col2:
                st.text(f"{file.size / 1024 / 1024:.2f} MB")
            with col3:
                if st.button("Upload", key=f"upload_{file.name}"):
                    with st.spinner(f"Uploading {file.name}..."):
                        try:
                            if SUPABASE_CREDS.get('available'):
                                headers = {
                                    'apikey': SUPABASE_CREDS['key'],
                                    'Authorization': f'Bearer {SUPABASE_CREDS["key"]}',
                                    'Content-Type': 'application/json',
                                    'Prefer': 'return=representation'
                                }
                                
                                dataset_data = {
                                    "filename": file.name,
                                    "size_mb": round(file.size / (1024 * 1024), 2),
                                    "rows": 0,
                                    "user_email": st.session_state.user_email,
                                    "uploaded_at": datetime.now().isoformat(),
                                    "status": "uploaded"
                                }
                                
                                response = requests.post(
                                    f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                                    headers=headers,
                                    json=dataset_data,
                                    timeout=TIMEOUT
                                )
                                
                                if response.status_code == 201:
                                    st.success(f"✅ {file.name} uploaded!")
                                    st.balloons()
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {response.status_code} - {response.text[:200]}")
                            else:
                                st.error("Supabase not configured")
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)[:100]}")

# List datasets
st.markdown("## 📋 Your Datasets")

with st.spinner("Loading datasets..."):
    datasets = fetch_datasets()

if not datasets:
    st.info("No datasets found. Upload some files!")
else:
    st.success(f"Found {len(datasets)} dataset(s)")
    
    for dataset in datasets:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{dataset.get('filename', 'Unnamed')}**")
                uploaded = dataset.get('uploaded_at', '')
                if uploaded:
                    if 'T' in uploaded:
                        date_part = uploaded.split('T')[0]
                    else:
                        date_part = uploaded[:10]
                    st.caption(f"Uploaded: {date_part}")
            
            with col2:
                rows = dataset.get('rows', 0)
                st.markdown(f"**{rows:,}**")
                st.caption("rows")
            
            with col3:
                if st.button("📊 Analyze", key=f"analyze_{dataset.get('id')}", use_container_width=True):
                    st.session_state.selected_dataset_id = dataset.get('id')
                    st.switch_page("pages/1_Analytics.py")
            
            with col4:
                if st.button("🗑️", key=f"delete_{dataset.get('id')}", use_container_width=True, help="Delete"):
                    st.warning(f"Delete {dataset.get('filename', 'this dataset')}?")
                    
            st.markdown("---")

st.markdown("---")
st.caption(f"📁 Data Management • {len(datasets)} datasets • {datetime.now().strftime('%H:%M:%S')}")