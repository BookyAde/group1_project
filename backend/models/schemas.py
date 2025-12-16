from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# --- Filtering Schema ---

class DataFilter(BaseModel):
    """
    Defines the filter criteria for requesting aggregated data from the backend.
    
    Fields here should correspond to common columns across your dataset or 
    to the metadata in your 'uploads' table.
    """
    # Use to specify which uploaded files (tables) should be included.
    # The value will be the 'table_name' from the 'uploads' metadata table.
    table_names: Optional[List[str]] = None 
    
    # Optional search term to filter data rows (e.g., a keyword search across JSONB)
    search_term: Optional[str] = None
    
    # Date range filters (assuming your data has a date/timestamp column)
    # Passed as ISO 8601 strings (e.g., "2024-01-01")
    start_date: Optional[str] = None 
    end_date: Optional[str] = None
    
    # Add any other specific filters relevant to your common data structure here.
    # Example:
    # user_id: Optional[str] = None 
    
    # Pagination/limit for large datasets
    limit: int = 1000  
    offset: int = 0
    # Add these Pydantic models to backend/models/schemas.py


class ETLJob(BaseModel):
    id: str
    name: str
    type: str
    status: str
    progress: int
    started: datetime
    completed: Optional[datetime] = None
    sources: List[str]
    triggered_by: str
    rows_processed: int = 0
    duration_seconds: float = 0

class ETLError(BaseModel):
    job_id: str
    message: str
    details: Optional[str] = None
    timestamp: datetime
    severity: str = "error"
    module: Optional[str] = None

class ETLMetrics(BaseModel):
    jobs_today: int
    success_rate: float
    avg_processing_minutes: float
    data_volume_gb: float
    rows_processed_total: int
    daily_success: Dict[str, float]