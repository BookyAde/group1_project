# frontend/utils/config.py
import os
import streamlit as st

def get_backend_url():
    """
    Determine backend URL based on environment.
    Priority: Streamlit secrets > Environment variable > Default local
    """
    
    # 1. Check Streamlit Cloud secrets first (production)
    if hasattr(st, 'secrets'):
        # Option A: Direct Supabase REST URL
        if 'SUPABASE_URL' in st.secrets:
            supabase_url = st.secrets['SUPABASE_URL']
            # Return Supabase REST endpoint
            return f"{supabase_url}/rest/v1"
        
        # Option B: Custom backend URL in secrets
        if 'BACKEND_URL' in st.secrets:
            return st.secrets['BACKEND_URL']
    
    # 2. Check environment variables
    env_backend = os.getenv('BACKEND_URL')
    if env_backend:
        return env_backend
    
    env_supabase = os.getenv('SUPABASE_URL')
    if env_supabase:
        return f"{env_supabase}/rest/v1"
    
    # 3. Default fallback (local development)
    return "http://localhost:8000/api/v1"

def get_supabase_credentials():
    """Get Supabase credentials for direct client use"""
    credentials = {'url': '', 'key': '', 'available': False}
    
    # Check Streamlit secrets first
    if hasattr(st, 'secrets'):
        if 'SUPABASE_URL' in st.secrets and 'SUPABASE_KEY' in st.secrets:
            credentials['url'] = st.secrets['SUPABASE_URL']
            credentials['key'] = st.secrets['SUPABASE_KEY']
            credentials['available'] = True
            credentials['source'] = 'secrets'
            return credentials
    
    # Check environment variables
    env_url = os.getenv('SUPABASE_URL')
    env_key = os.getenv('SUPABASE_KEY')
    
    if env_url and env_key:
        credentials['url'] = env_url
        credentials['key'] = env_key
        credentials['available'] = True
        credentials['source'] = 'env'
        return credentials
    
    return credentials

# Global config variables
BACKEND_URL = get_backend_url()
SUPABASE_CREDS = get_supabase_credentials()
TIMEOUT = 30

# Debug info (remove in production)
def debug_info():
    """Show debug information"""
    info = {
        'backend_url': BACKEND_URL,
        'supabase_available': SUPABASE_CREDS['available'],
        'environment': 'production' if 'STREAMLIT_CLOUD' in os.environ else 'development',
        'has_secrets': hasattr(st, 'secrets') if 'st' in locals() else False
    }
    return info