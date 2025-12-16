# 📄 backend/core/config.py - UPDATED WITH BACKEND_URL

from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import Optional

load_dotenv()

class Settings:
    PROJECT_NAME = "Data Platform Backend"
    API_VERSION = "v1"
    
    # ✅ ADD THIS: Backend configuration
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")
    
    # File upload settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "csv,xlsx,xls").split(",")
    
    # Supabase settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_development(self):
        return self.ENVIRONMENT == "development"

settings = Settings()

# Private module-level storage
_supabase_anon: Optional[Client] = None
_supabase_service: Optional[Client] = None

def init_supabase() -> None:
    """Initialize Supabase clients once at startup."""
    global _supabase_anon, _supabase_service

    if not all([
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        settings.SUPABASE_SERVICE_KEY
    ]):
        print("⚠️ Supabase env vars missing — clients not initialized")
        return

    _supabase_anon = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )
    _supabase_service = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )

    print("✅ Supabase clients initialized")

def get_supabase_anon() -> Client:
    if _supabase_anon is None:
        raise RuntimeError("Supabase anon client not initialized")
    return _supabase_anon

def get_supabase_service() -> Client:
    if _supabase_service is None:
        raise RuntimeError("Supabase service client not initialized")
    return _supabase_service

# ✅ THIS IS THE MISSING PIECE
def initialize_supabase_clients() -> None:
    init_supabase()