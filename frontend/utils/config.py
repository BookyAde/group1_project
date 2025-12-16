# frontend/utils/config.py
import os
import sys

def safe_get_secrets():
    """Safely get Streamlit secrets without raising errors"""
    try:
        import streamlit as st
        
        # Check if we're in a proper Streamlit context
        if not hasattr(st, 'secrets'):
            return {}
            
        # Try to access secrets - handle missing file gracefully
        try:
            # This will only work if secrets.toml exists and is valid
            if st.secrets:
                return dict(st.secrets)
        except Exception:
            # File doesn't exist or is invalid
            return {}
            
    except ImportError:
        # streamlit module not available
        pass
        
    return {}

def get_backend_url():
    """Get backend URL with multiple fallbacks"""
    
    # Get secrets safely
    secrets = safe_get_secrets()
    
    # Priority 1: Secrets file
    if 'SUPABASE_URL' in secrets:
        supabase_url = secrets['SUPABASE_URL']
        if supabase_url and supabase_url.strip():
            return f"{supabase_url}/rest/v1"
    
    if 'BACKEND_URL' in secrets:
        backend_url = secrets['BACKEND_URL']
        if backend_url and backend_url.strip():
            return backend_url
    
    # Priority 2: Environment variables
    env_supabase = os.getenv('SUPABASE_URL')
    if env_supabase:
        return f"{env_supabase}/rest/v1"
    
    env_backend = os.getenv('BACKEND_URL')
    if env_backend:
        return env_backend
    
    # Priority 3: Check for .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_supabase = os.getenv('SUPABASE_URL')
        if env_supabase:
            return f"{env_supabase}/rest/v1"
            
        env_backend = os.getenv('BACKEND_URL')
        if env_backend:
            return env_backend
    except ImportError:
        pass
    
    # Priority 4: Default fallback
    return "http://localhost:8000/api/v1"

def get_supabase_credentials():
    """Get Supabase credentials with multiple fallbacks"""
    credentials = {
        'url': '',
        'key': '',
        'available': False,
        'source': 'none'
    }
    
    # 1. Try secrets file
    secrets = safe_get_secrets()
    if 'SUPABASE_URL' in secrets and 'SUPABASE_KEY' in secrets:
        url = secrets['SUPABASE_URL']
        key = secrets['SUPABASE_KEY']
        if url and key and url.strip() and key.strip():
            credentials['url'] = url
            credentials['key'] = key
            credentials['available'] = True
            credentials['source'] = 'secrets'
            return credentials
    
    # 2. Try environment variables
    env_url = os.getenv('SUPABASE_URL')
    env_key = os.getenv('SUPABASE_KEY')
    
    if env_url and env_key:
        credentials['url'] = env_url
        credentials['key'] = env_key
        credentials['available'] = True
        credentials['source'] = 'env'
        return credentials
    
    # 3. Try .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_url = os.getenv('SUPABASE_URL')
        env_key = os.getenv('SUPABASE_KEY')
        
        if env_url and env_key:
            credentials['url'] = env_url
            credentials['key'] = env_key
            credentials['available'] = True
            credentials['source'] = 'dotenv'
            return credentials
    except ImportError:
        pass
    
    return credentials

# Initialize - these won't crash if secrets are missing
BACKEND_URL = get_backend_url()
SUPABASE_CREDS = get_supabase_credentials()
TIMEOUT = 30

# Safe debug function
def debug_info():
    """Show debug information without crashing"""
    info = {
        'backend_url': BACKEND_URL,
        'supabase_available': SUPABASE_CREDS['available'],
        'supabase_source': SUPABASE_CREDS['source'],
        'python_version': sys.version[:20],
        'cwd': os.getcwd()
    }
    
    # Safely add Streamlit info
    try:
        import streamlit as st
        info['has_streamlit'] = True
        info['streamlit_version'] = st.__version__
    except ImportError:
        info['has_streamlit'] = False
        
    return info