import requests
import streamlit as st
from typing import Dict, Any 

# Set the base URL for the FastAPI backend
API_BASE_URL = "http://localhost:8000/api/v1"

# Helper function to safely parse response and handle connection errors
def handle_response(response: requests.Response, success_message: str):
    """Safely handles API response, checks status, and attempts JSON parsing."""
    try:
        # Check if response content type indicates JSON
        is_json = 'application/json' in response.headers.get('Content-Type', '').lower()
        
        if response.status_code == 200:
            if is_json:
                return True, response.json()
            # Status 200, but not JSON (e.g., plain text OK), treat as unexpected
            return False, f"Unexpected success response format (Status 200, Content-Type: {response.headers.get('Content-Type', 'None')})"

        # Handle non-200 status codes
        if is_json:
            # Assume FastAPI returned error detail in JSON
            data = response.json()
            return False, data.get("detail", f"API Error (Status {response.status_code}): {data}")
        else:
            # Server communication error (e.g., 500 HTML page, or non-JSON 404/401)
            return False, f"Server communication error (Status {response.status_code}): {response.text[:200]}..."
            
    except requests.exceptions.JSONDecodeError:
        return False, f"Connection error: Failed to decode JSON response. Received non-JSON body: {response.text[:100]}..."
    except Exception as e:
        return False, f"Client Error during response handling: {str(e)}"


class APIClient:
    """Client for interacting with the FastAPI backend via HTTP."""
    
    def __init__(self):
        # Initialize session state variables if they don't exist
        if 'access_token' not in st.session_state:
            st.session_state['access_token'] = None
        if 'user_info' not in st.session_state:
            st.session_state['user_info'] = {}
        
        self.base_url = API_BASE_URL
        self._token = st.session_state['access_token']
        self._user_info = st.session_state['user_info']

    def _get_headers(self):
        """Constructs headers with Authorization if token exists."""
        self._token = st.session_state.get('access_token')
        
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def _update_session(self, token: str, user_info: dict = None):
        """Updates session state after successful login."""
        st.session_state['access_token'] = token
        if user_info:
            st.session_state['user_info'] = user_info
        self._token = token
        self._user_info = user_info

    def _clear_session(self):
        """Clears session state upon logout."""
        st.session_state['access_token'] = None
        st.session_state['user_info'] = {}
        self._token = None
        self. _user_info = {}

    # --- API Methods using handle_response ---

    def signup(self, email: str, password: str):
        """Sign up a new user via backend API."""
        try:
            url = f"{self.base_url}/auth/signup"
            response = requests.post(url, json={"email": email, "password": password})
            return handle_response(response, "Signup successful!")
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"

    def login(self, email: str, password: str):
        """Login user via backend API."""
        try:
            url = f"{self.base_url}/auth/login"
            response = requests.post(url, json={"email": email, "password": password})
            success, data = handle_response(response, "Login successful!")
            
            if success and isinstance(data, dict):
                # Custom logic for login success: update session
                self._update_session(
                    token=data.get('access_token'),
                    user_info=data.get('user')
                )
                return True, "Login successful!"
            else:
                return success, data
                
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"
        
    def logout(self):
        """Clear session state."""
        self._clear_session()

    def upload_data(self, file_bytes: bytes, filename: str):
        """Upload file to backend."""
        try:
            url = f"{self.base_url}/data/upload"
            files = {'file': (filename, file_bytes)}
            headers = self._get_headers()
            
            response = requests.post(url, files=files, headers=headers, timeout=60)
            return handle_response(response, "File uploaded successfully")
                
        except requests.exceptions.Timeout:
            return False, "Upload timeout. File might be too large."
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"

    def get_processed_data(self):
        """Retrieve all processed data metadata for the current user."""
        return self.list_datasets() 

    def list_datasets(self):
        """List all dataset metadata for the current user."""
        try:
            url = f"{self.base_url}/data/list"
            headers = self._get_headers()
            response = requests.get(url, headers=headers)
            return handle_response(response, "Datasets listed successfully")
                
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"
            
    def get_file_data(self, upload_id: str, limit: int = 1000):
        """Fetches a preview of the raw data contents for a specific upload ID."""
        try:
            url = f"{self.base_url}/data/file/{upload_id}"
            headers = self._get_headers()
            # FIXED: Use params instead of string interpolation
            params = {"limit": limit}
            response = requests.get(url, headers=headers, params=params)
            return handle_response(response, "File data retrieved successfully")
                
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"

    def get_task_status(self, task_id: str):
        """Check the status of a background ETL job."""
        try:
            url = f"{self.base_url}/data/status/{task_id}"
            headers = self._get_headers()
            response = requests.get(url, headers=headers)
            return handle_response(response, "Task status retrieved successfully")
                
        except requests.exceptions.RequestException as e:
            return False, f"Network/Connection error: {str(e)}"


@st.cache_resource
def get_api_client_v3(): 
    """Factory function to create and cache the APIClient instance."""
    return APIClient()

@st.cache_resource  # Also cache this for performance
def get_api_client():
    """Backward compatibility function - use get_api_client_v3() for new code."""
    return get_api_client_v3()