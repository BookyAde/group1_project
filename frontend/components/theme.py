# -*- coding: utf-8 -*-
import streamlit as st

class WarehouseTheme:
    @staticmethod
    def apply_global_styles():
        """Apply custom CSS for gold & black theme"""
        st.markdown("""
        <style>
        /* Main background and text */
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #ffffff;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FFD700 !important;
            font-weight: 700;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1a1a1a;
            border-right: 2px solid #FFD700;
        }
        
        /* Sidebar text */
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            color: #000000 !important;
            border: none;
            font-weight: bold;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #FFA500 0%, #FF8C00 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
        }
        
        /* Primary button */
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(90deg, #FFD700 0%, #FF8C00 100%) !important;
            color: #000000 !important;
        }
        
        /* Metric cards */
        div[data-testid="stMetric"] {
            background-color: #222222;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #FFD700;
        }
        
        /* Dataframes */
        .dataframe {
            background-color: #222222 !important;
            color: #ffffff !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            background-color: #222222 !important;
            color: #ffffff !important;
            border: 1px solid #FFD700 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #222222;
            color: #ffffff;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #FFD700 !important;
            color: #000000 !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #222222;
            color: #FFD700 !important;
            border: 1px solid #FFD700;
            border-radius: 8px;
        }
        
        /* Success/Error/Info boxes */
        .stAlert {
            background-color: #222222;
            border-left: 4px solid;
            border-radius: 8px;
        }
        
        .stAlert [data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background-color: #FFD700;
        }
        
        /* Code blocks */
        .stCodeBlock {
            background-color: #222222;
            border: 1px solid #FFD700;
        }
        
        /* Footer text */
        .stCaption {
            color: #888888 !important;
        }
        
        /* Links */
        a {
            color: #FFD700 !important;
        }
        
        /* Divider */
        hr {
            border-color: #FFD700;
            opacity: 0.5;
        }
        
        /* Tooltips */
        [data-testid="stTooltip"] {
            background-color: #222222 !important;
            color: #ffffff !important;
            border: 1px solid #FFD700 !important;
        }
        
        /* Toast notifications */
        .toast-notification {
            background-color: #222222 !important;
            color: #ffffff !important;
            border-left: 4px solid #FFD700 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_light_styles():
        """Light theme variant"""
        st.markdown("""
        <style>
        .stApp { background: #f8f9fa; color: #333333; }
        h1, h2, h3 { color: #1a1a1a !important; }
        section[data-testid="stSidebar"] { background-color: #ffffff; }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_blue_styles():
        """Blue theme variant"""
        st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: #ffffff; }
        h1, h2, h3 { color: #87CEFA !important; }
        section[data-testid="stSidebar"] { background-color: #2a5298; }
        </style>
        """, unsafe_allow_html=True)