# 📄 frontend/components/sidebar.py - SIMPLIFIED

import streamlit as st
from datetime import datetime

def render_sidebar():
    """Render the gold/black themed sidebar without navigation buttons"""
    
    with st.sidebar:
        # Sidebar Header
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #000000 0%, #343A40 100%);
            padding: 1.5rem;
            border-radius: 0 0 12px 12px;
            margin: -1rem -1rem 1rem -1rem;
            text-align: center;
        ">
            <h1 style="color: #FFD700; margin: 0; font-size: 1.8rem;">🏭</h1>
            <h2 style="color: #FFFFFF; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Data Warehouse Simulation
            </h2>
            <p style="color: #ADB5BD; margin: 0.25rem 0 0 0; font-size: 0.8rem;">
                v2.0 • {datetime.now().strftime('%Y-%m-%d')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ✅ Streamlit automatically adds page navigation here!
        
        st.markdown("---")
        
        # System Status
        st.markdown("### ⚡ System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API", "✅", "Online")
        with col2:
            st.metric("Database", "✅", "Connected")
        
        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        
        if 'total_files' in st.session_state:
            st.metric("Total Files", f"{st.session_state.total_files:,}")
        if 'total_rows' in st.session_state:
            st.metric("Data Rows", f"{st.session_state.total_rows:,}")
        
        st.markdown("---")
        
        # User Info
        if 'user_email' in st.session_state:
            st.markdown(f"""
            <div style="
                background: rgba(255, 215, 0, 0.1);
                padding: 1rem;
                border-radius: 8px;
                border-left: 3px solid #FFD700;
            ">
                <div style="color: #FFD700; font-weight: 600;">👤 User</div>
                <div style="color: #FFFFFF; font-size: 0.9rem;">
                    {st.session_state.user_email}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                # Clear session but keep essential data
                keys_to_keep = ['theme', 'initialized']
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                st.session_state.user_email = None
                st.rerun()
        else:
            if st.button("🔐 Login", key="sidebar_login", use_container_width=True, type="primary"):
                st.switch_page("app.py")
        
        # Footer
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")