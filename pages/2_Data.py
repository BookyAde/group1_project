# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import requests
from io import BytesIO

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
            st.write("📁 Data Management")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30

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

# Fetch current datasets
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

# Upload section
st.markdown("## 📤 Upload to Backend")

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
                            files = {"file": (file.name, file.getvalue())}
                            response = requests.post(
                                f"{BACKEND_URL}/data/upload",
                                files=files,
                                timeout=TIMEOUT
                            )
                            
                            if response.status_code == 200:
                                st.success(f"✅ {file.name} uploaded successfully!")
                                st.balloons()
                                st.cache_data.clear()  # Clear cache to refresh datasets
                                st.rerun()
                            else:
                                st.error(f"Upload failed: {response.status_code}")
                        except Exception as e:
                            st.error(f"Upload error: {str(e)[:100]}")

with upload_tab2:
    st.markdown("Create sample data for testing:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Sales Data", use_container_width=True):
            # Create sample sales data
            import numpy as np
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            sample_df = pd.DataFrame({
                'date': dates,
                'product': ['Product ' + str(i % 5 + 1) for i in range(100)],
                'sales': np.random.normal(10000, 2000, 100),
                'quantity': np.random.randint(50, 200, 100)
            })
            
            # Convert to CSV bytes
            csv_bytes = sample_df.to_csv(index=False).encode()
            files = {"file": ("sample_sales.csv", csv_bytes)}
            
            with st.spinner("Creating sample sales data..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/data/upload", files=files, timeout=TIMEOUT)
                    if response.status_code == 200:
                        st.success("✅ Sample sales data created!")
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")

# List datasets
st.markdown("## 📋 Your Datasets")

with st.spinner("Loading datasets..."):
    datasets = fetch_datasets()

if not datasets:
    st.info("No datasets uploaded yet. Use the upload section above to add data.")
else:
    # Search and filter
    search_term = st.text_input("🔍 Search datasets:", placeholder="Filter by name...")
    
    # Filter datasets
    filtered_datasets = datasets
    if search_term:
        filtered_datasets = [d for d in datasets if search_term.lower() in d.get('filename', '').lower()]
    
    st.success(f"Found {len(filtered_datasets)} dataset(s)")
    
    # Display as cards
    for dataset in filtered_datasets:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{dataset.get('filename')}**")
                st.caption(f"ID: {dataset.get('id', 'N/A')[:8]}... • Uploaded: {dataset.get('uploaded_at', '')[:10]}")
            
            with col2:
                st.markdown(f"**{dataset.get('rows', 0):,}**")
                st.caption("rows")
            
            with col3:
                if st.button("📊 Analyze", key=f"analyze_{dataset.get('id')}", use_container_width=True):
                    st.session_state.selected_dataset_id = dataset.get('id')
                    st.switch_page("pages/1_Analytics.py")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{dataset.get('id')}", use_container_width=True):
                    st.warning(f"Delete {dataset.get('filename')}?")
                    if st.button("Confirm Delete", key=f"confirm_{dataset.get('id')}"):
                        # Note: You need to implement DELETE endpoint in backend
                        st.info("Delete feature coming soon...")
                        # response = requests.delete(f"{BACKEND_URL}/data/{dataset.get('id')}")
                        # if response.status_code == 200:
                        #     st.success("Dataset deleted")
                        #     st.cache_data.clear()
                        #     st.rerun()
            
            st.markdown("---")

# Update session stats
if 'total_files' in st.session_state:
    st.session_state.total_files = len(datasets)
    st.session_state.total_rows = sum(d.get('rows', 0) for d in datasets)

st.markdown("---")
st.caption(f"📁 Data Management • {len(datasets)} datasets • {datetime.now().strftime('%H:%M:%S')}")