# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import requests
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --------------------------------------------------
# Safe imports with fallbacks
# --------------------------------------------------
try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT, SUPABASE_CREDS
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles():
            pass

    def render_sidebar():
        with st.sidebar:
            st.write("⚙️ Settings")

    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30
    SUPABASE_CREDS = {'available': False, 'url': '', 'key': ''}

# --------------------------------------------------
# Apply Theme (IMPORTANT - do this early)
# --------------------------------------------------
try:
    from frontend.components.theme import WarehouseTheme
    WarehouseTheme.apply_theme()
except:
    pass

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Settings - Data Warehouse",
    page_icon="⚙️",
    layout="wide"
)

# --------------------------------------------------
# Auth Guard
# --------------------------------------------------
if 'user_email' not in st.session_state:
    # Auto-login for development
    st.session_state.user_email = "demo@datawarehouse.com"
    if 'access_token' not in st.session_state:
        st.session_state.access_token = "demo_token_12345"
    st.rerun()

# Ensure access_token exists
if 'access_token' not in st.session_state:
    st.session_state.access_token = "demo_token_12345"

# --------------------------------------------------
# Helper: Fetch datasets from Supabase
# --------------------------------------------------
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
                params={'select': '*'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        else:
            # Fallback to original backend
            response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                return data.get('datasets', [])
                
    except Exception as e:
        st.error(f"Failed to fetch datasets: {str(e)[:100]}")
        return []

# --------------------------------------------------
# Initialize settings with defaults
# --------------------------------------------------
if "app_settings" not in st.session_state:
    st.session_state.app_settings = {
        "theme": "gold",
        "theme_display": "Gold & Black",
        "auto_refresh": True,
        "refresh_interval": 30,
        "notifications": True,
        "max_file_size": 10,
        "data_retention_days": 30,
        "email_alerts": False,
        "default_page": "home"
    }

# Also ensure theme is in session state
if "theme" not in st.session_state:
    st.session_state.theme = st.session_state.app_settings.get("theme", "gold")

try:
    render_sidebar()
except Exception as e:
    st.sidebar.error(f"Sidebar error: {e}")

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">⚙️ System Settings</h1>
        <p style="margin-top: 0.5rem; opacity: 0.9;">
            Configure your Data Warehouse application
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------------------------------------
# Backend Status
# --------------------------------------------------
st.markdown("### 🔗 Backend Status")

try:
    if SUPABASE_CREDS.get('available'):
        headers = {
            'apikey': SUPABASE_CREDS['key'],
            'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
        }
        
        response = requests.get(
            f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
            headers=headers,
            params={'select': 'count'},
            timeout=5
        )
        
        if response.status_code == 200:
            datasets = fetch_datasets()
            st.success(f"✅ Supabase connected: {len(datasets)} datasets")
            
            with st.expander("Supabase Details"):
                info = {
                    "url": SUPABASE_CREDS['url'],
                    "status": "Connected",
                    "datasets_count": len(datasets),
                    "credentials_source": SUPABASE_CREDS.get('source', 'unknown')
                }
                st.json(info)
                
                # Show first few datasets
                if datasets:
                    st.markdown("**Recent datasets:**")
                    for dataset in datasets[:3]:
                        st.write(f"- {dataset.get('filename', 'Unknown')} ({dataset.get('rows', 0)} rows)")
        else:
            st.warning(f"⚠️ Supabase error: {response.status_code}")
            
    else:
        st.warning("⚠️ Supabase not configured")
        st.info("Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml")

except Exception as e:
    st.error(f"❌ Connection error: {str(e)[:100]}")

st.markdown("---")

# --------------------------------------------------
# Appearance Settings
# --------------------------------------------------
st.markdown("### 🎨 Appearance")

col1, col2 = st.columns(2)

with col1:
    # Theme selection
    theme_display = st.selectbox(
        "Theme",
        ["Gold & Black", "Dark", "Light", "Blue"],
        index=["Gold & Black", "Dark", "Light", "Blue"].index(
            st.session_state.app_settings.get("theme_display", "Gold & Black")
        )
    )

    # Auto-refresh settings
    auto_refresh = st.checkbox(
        "Enable auto-refresh",
        value=st.session_state.app_settings["auto_refresh"]
    )

    # Refresh interval (only shown if auto-refresh is enabled)
    refresh_interval = st.session_state.app_settings["refresh_interval"]
    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh interval (seconds)",
            5, 300, refresh_interval
        )

with col2:
    # Notification settings
    notifications = st.checkbox(
        "Enable notifications",
        value=st.session_state.app_settings["notifications"]
    )
    
    # Email alerts
    email_alerts = st.checkbox(
        "Email alerts for critical events",
        value=st.session_state.app_settings.get("email_alerts", False)
    )

    # Max file size
    max_file_size = st.slider(
        "Max file upload size (MB)",
        1, 100, st.session_state.app_settings["max_file_size"]
    )
    
    # Data retention
    data_retention_days = st.slider(
        "Data retention (days)",
        1, 365, st.session_state.app_settings.get("data_retention_days", 30)
    )

st.markdown("---")

# --------------------------------------------------
# System Actions
# --------------------------------------------------
st.markdown("### ⚡ System Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared successfully!")
        st.rerun()

with col2:
    if st.button("📊 Refresh Stats", use_container_width=True):
        datasets = fetch_datasets()
        st.session_state.total_files = len(datasets)
        st.session_state.total_rows = sum(d.get("rows", 0) for d in datasets)
        st.success(f"Stats refreshed: {len(datasets)} datasets")
        st.rerun()

with col3:
    if st.button("📋 Export Logs", use_container_width=True):
        # Get datasets count
        datasets = fetch_datasets()
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.user_email,
            "settings": st.session_state.app_settings,
            "datasets_count": len(datasets),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "streamlit_version": st.__version__
            },
            "supabase_status": {
                "available": SUPABASE_CREDS.get('available', False),
                "source": SUPABASE_CREDS.get('source', 'none'),
                "url": SUPABASE_CREDS.get('url', '')
            }
        }

        # Create download button
        st.download_button(
            label="📥 Download Logs",
            data=json.dumps(log_data, indent=2),
            file_name=f"warehouse_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")

# --------------------------------------------------
# Advanced Settings
# --------------------------------------------------
with st.expander("⚙️ Advanced Settings", expanded=False):
    st.markdown("### Advanced Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_page = st.selectbox(
            "Default landing page",
            ["Home", "Analytics", "Data", "ETL", "Settings"],
            index=["Home", "Analytics", "Data", "ETL", "Settings"].index(
                st.session_state.app_settings.get("default_page", "Home").title()
            )
        )
        
        session_timeout = st.slider(
            "Session timeout (minutes)",
            15, 480, 60
        )
    
    with col2:
        api_timeout = st.slider(
            "API timeout (seconds)",
            10, 300, 30
        )
        
        enable_analytics = st.checkbox(
            "Enable usage analytics",
            value=True
        )
    
    # Connection test
    st.markdown("### 🔌 Connection Test")
    if st.button("Test Supabase Connection"):
        try:
            if SUPABASE_CREDS.get('available'):
                headers = {
                    'apikey': SUPABASE_CREDS['key'],
                    'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
                }
                
                response = requests.get(
                    f"{SUPABASE_CREDS['url']}/rest/v1/",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    st.success("✅ Supabase connection successful!")
                else:
                    st.error(f"❌ Supabase error: {response.status_code}")
            else:
                st.warning("⚠️ Supabase not configured")
                
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)[:100]}")
    
    # Danger zone
    st.markdown("### ⚠️ Danger Zone")
    if st.button("🛑 Reset All Settings", type="secondary"):
        st.warning("This will reset all settings to defaults!")
        confirm = st.checkbox("I understand this action cannot be undone")
        if confirm and st.button("Confirm Reset", type="primary"):
            st.session_state.app_settings = {
                "theme": "gold",
                "theme_display": "Gold & Black",
                "auto_refresh": True,
                "refresh_interval": 30,
                "notifications": True,
                "max_file_size": 10,
                "data_retention_days": 30,
                "email_alerts": False,
                "default_page": "home"
            }
            st.session_state.theme = "gold"
            try:
                from frontend.components.theme import WarehouseTheme
                WarehouseTheme.apply_theme("gold")
            except:
                pass
            st.success("All settings have been reset to defaults!")
            st.rerun()

st.markdown("---")

# --------------------------------------------------
# Save Settings
# --------------------------------------------------
if st.button("💾 Save All Settings", type="primary", use_container_width=True):
    # Map display name to theme key
    theme_map = {
        "Gold & Black": "gold",
        "Dark": "dark",
        "Light": "light",
        "Blue": "blue"
    }
    
    theme_key = theme_map[theme_display]
    
    # Update all settings
    st.session_state.app_settings.update({
        "theme": theme_key,
        "theme_display": theme_display,
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval if auto_refresh else 30,
        "notifications": notifications,
        "email_alerts": email_alerts,
        "max_file_size": max_file_size,
        "data_retention_days": data_retention_days,
        "default_page": default_page.lower(),
        "session_timeout": session_timeout,
        "api_timeout": api_timeout,
        "enable_analytics": enable_analytics
    })
    
    # Apply new theme immediately
    st.session_state.theme = theme_key
    try:
        from frontend.components.theme import WarehouseTheme
        WarehouseTheme.apply_theme(theme_key)
    except:
        pass
    
    st.success("✅ All settings saved successfully!")
    st.balloons()
    st.rerun()

# --------------------------------------------------
# Current Settings Display
# --------------------------------------------------
with st.expander("📋 Current Settings Summary", expanded=False):
    st.markdown("### Current Configuration")
    
    # Display current settings
    settings_df = pd.DataFrame(
        [(k.replace('_', ' ').title(), v) for k, v in st.session_state.app_settings.items()],
        columns=["Setting", "Value"]
    )
    st.dataframe(settings_df, use_container_width=True, hide_index=True)
    
    # System info
    st.markdown("### System Information")
    system_info = {
        "User": st.session_state.user_email,
        "Python Version": sys.version.split()[0],
        "Streamlit Version": st.__version__,
        "Platform": sys.platform,
        "Supabase Configured": SUPABASE_CREDS.get('available', False),
        "Total Datasets": st.session_state.get('total_files', 0)
    }
    
    for key, value in system_info.items():
        st.write(f"**{key}:** {value}")

st.markdown("---")
st.caption(
    f"⚙️ Settings • User: {st.session_state.user_email} • "
    f"Theme: {st.session_state.app_settings.get('theme_display', 'Gold & Black')} • "
    f"{datetime.now().strftime('%H:%M:%S')}"
)