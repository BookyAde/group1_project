# -*- coding: utf-8 -*-
import os

class Config:
    """Central configuration for the frontend"""
    
    # Backend URL - Single source of truth
    BACKEND_URL = "http://localhost:8000/api/v1"
    
    # API Timeout
    TIMEOUT = 30
    
    # App settings
    APP_NAME = "Data Warehouse Simulation"
    APP_VERSION = "2.0"
    
    @staticmethod
    def get_backend_url(endpoint=""):
        """Get full backend URL for an endpoint"""
        return f"{Config.BACKEND_URL}/{endpoint.lstrip('/')}"
    
    @staticmethod
    def test_connection():
        """Test if backend is accessible"""
        import requests
        try:
            response = requests.get(f"{Config.BACKEND_URL}/data/list", timeout=5)
            return response.status_code == 200, response.json().get('count', 0) if response.status_code == 200 else 0
        except:
            return False, 0

# Export
BACKEND_URL = Config.BACKEND_URL
TIMEOUT = Config.TIMEOUT