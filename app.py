# 📄 app.py - SIMPLIFIED (No custom navigation)

import streamlit as st
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config - MUST BE FIRST
st.set_page_config(
    page_title="Data Warehouse Simulation",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for login persistence
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# For testing: Auto-login as demo
if st.session_state.user_email is None and 'autologin_done' not in st.session_state:
    st.session_state.autologin_done = True
    st.session_state.user_email = "demo@datawarehouse.com"
    st.session_state.user_info = {
        "email": "demo@datawarehouse.com",
        "name": "Demo User"
    }
    st.session_state.total_files = 0
    st.session_state.total_rows = 0
    st.session_state.total_size_mb = 0.0
    st.rerun()

# Import after path setup
try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
except ImportError as e:
    st.error(f"Import error: {e}")
    # Create fallback components
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles():
            st.markdown("""
            <style>
            .stApp { background: white; color: black; }
            h1, h2, h3 { color: #000000; }
            </style>
            """, unsafe_allow_html=True)
    
    def render_sidebar():
        with st.sidebar:
            st.write("📊 Data Warehouse Simulation")

# Apply theme
WarehouseTheme.apply_global_styles()

# Render sidebar
render_sidebar()

# Main content
if st.session_state.user_email:
    st.title("🏭 Data Warehouse Simulation")
    st.markdown("---")
    
    st.success(f"✅ Welcome, **{st.session_state.user_email}**!")
    
    st.info(f"""
    ### Welcome to Data Warehouse Simulation Platform
    
    👈 **Use the sidebar to navigate between pages:**
    
    **Available Pages:**
    1. **🏠 Home** - Overview and key metrics
    2. **📊 Analytics** - Data visualization and insights  
    3. **📁 Data Management** - Upload and manage datasets
    4. **🔄 ETL Monitor** - Pipeline monitoring and control
    5. **⚙️ Settings** - Configuration and preferences
    
    **Features:**
    - Real-time data processing
    - ETL pipeline monitoring
    - Interactive analytics
    - Data quality checks
    - Automated reporting
    
    **Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "🟢 Online", "Active")
        
    with col2:
        st.metric("Data Volume", f"{st.session_state.get('total_size_mb', 0)/1024:.2f} GB", "Ready")
        
    with col3:
        st.metric("User", "Logged in", st.session_state.user_email.split('@')[0])
        
    # Logout button
    if st.button("Logout"):
        st.session_state.user_email = None
        st.session_state.user_info = {}
        st.rerun()
        
else:
    # Login form
    st.title("🔐 Login Required")
    st.markdown("---")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        col_a, col_b = st.columns(2)
        with col_a:
            login_btn = st.form_submit_button("Login", type="primary", use_container_width=True)
        with col_b:
            demo_btn = st.form_submit_button("Demo Login", use_container_width=True)
        
        if login_btn or demo_btn:
            if demo_btn:
                email = "demo@datawarehouse.com"
            
            if email:
                st.session_state.user_email = email
                st.session_state.user_info = {
                    "email": email,
                    "name": email.split('@')[0].title()
                }
                st.success(f"Welcome {email.split('@')[0]}!")
                st.rerun()
            else:
                st.error("Please enter an email")

# Footer
st.markdown("---")
st.caption(f"Data Warehouse Simulation v2.0 • Professional Edition • {datetime.now().strftime('%H:%M:%S')}")