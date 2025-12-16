import pandas as pd
from io import BytesIO
from typing import List, Dict, Any
from supabase import Client 
import numpy as np 
import uuid 
import logging
from datetime import datetime, timedelta
import time

from fastapi import HTTPException
from backend.core.config import get_supabase_service
from backend.models.schemas import DataFilter
# backend/services/etl.py (update with these methods)
from typing import List, Dict, Optional
import json
import uuid
from ..models.schemas import ETLJob, ETLError, ETLMetrics

class ETLServices:
    # In-memory storage (replace with database in production)
    _jobs = []
    _errors = []
    _metrics = {}
    
    @classmethod
    def execute_pipeline(cls, pipeline_type: str = "full", sources: List[str] = None):
        """Execute ETL pipeline"""
        job_id = str(uuid.uuid4())[:8]
        
        job = {
            "id": f"ETL-{job_id}",
            "name": f"{pipeline_type.title()} Pipeline",
            "type": pipeline_type,
            "status": "running",
            "progress": 0,
            "started": datetime.now().isoformat(),
            "sources": sources or [],
            "triggered_by": "system",
            "rows_processed": 0,
            "duration_seconds": 0
        }
        
        cls._jobs.append(job)
        
        # Simulate ETL process (replace with actual logic)
        # This is where you'd call your actual ETL functions
        
        return job
    
    @classmethod
    def get_job_history(cls, limit: int = 50, status_filter: Optional[str] = None):
        """Get ETL job history with optional filtering"""
        jobs = cls._jobs.copy()
        
        if status_filter:
            jobs = [j for j in jobs if j.get("status") == status_filter]
        
        # Sort by most recent
        jobs.sort(key=lambda x: x.get("started", ""), reverse=True)
        
        return jobs[:limit]
    
    @classmethod
    def calculate_metrics(cls, days: int = 7):
        """Calculate ETL performance metrics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_jobs = [
            j for j in cls._jobs 
            if datetime.fromisoformat(j.get("started", "2000-01-01")) > cutoff_date
        ]
        
        if not recent_jobs:
            return {
                "jobs_today": 0,
                "success_rate": 100,
                "avg_processing_minutes": 0,
                "data_volume_gb": 0,
                "rows_processed_total": 0
            }
        
        # Calculate metrics
        completed_jobs = [j for j in recent_jobs if j.get("status") == "completed"]
        failed_jobs = [j for j in recent_jobs if j.get("status") == "failed"]
        
        success_rate = (len(completed_jobs) / len(recent_jobs)) * 100 if recent_jobs else 100
        
        total_rows = sum(j.get("rows_processed", 0) for j in recent_jobs)
        
        return {
            "jobs_today": len(recent_jobs),
            "success_rate": round(success_rate, 1),
            "avg_processing_minutes": 5.2,  # Replace with actual calculation
            "data_volume_gb": round(total_rows * 0.000001, 2),  # Example calculation
            "rows_processed_total": total_rows,
            "daily_success": {  # Sample data
                (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"): 95 + (i % 5)
                for i in range(7)
            }
        }
    
    @classmethod
    def get_recent_errors(cls, limit: int = 20):
        """Get recent ETL errors"""
        errors = cls._errors.copy()
        errors.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return errors[:limit]
    
    @classmethod
    def log_error(cls, job_id: str, error_message: str, details: str = None):
        """Log ETL error"""
        error = {
            "job_id": job_id,
            "message": error_message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "severity": "error"
        }
        cls._errors.append(error)
        return error
    
    @classmethod
    def queue_etl_job(cls, pipeline_type: str, sources: List[str]):
        """Queue ETL job for background execution"""
        job_id = str(uuid.uuid4())[:8]
        
        job = {
            "id": f"ETL-{job_id}",
            "name": f"{pipeline_type.title()} Pipeline",
            "type": pipeline_type,
            "status": "queued",
            "sources": sources,
            "queued_at": datetime.now().isoformat()
        }
        
        cls._jobs.append(job)
        return job["id"]
    
    @classmethod
    def execute_queued_job(cls, job_id: str):
        """Execute a queued ETL job"""
        # Find and update job
        for job in cls._jobs:
            if job["id"] == job_id:
                job["status"] = "running"
                job["started"] = datetime.now().isoformat()
                # Execute actual ETL logic here
                # ...
                job["status"] = "completed"
                job["completed_at"] = datetime.now().isoformat()
                break
    
    @classmethod
    def create_schedule(cls, schedule_type: str, run_time: Optional[str], sources: List[str]):
        """Create ETL schedule"""
        schedule_id = str(uuid.uuid4())[:8]
        
        # Store schedule (in production, use database)
        schedule = {
            "id": schedule_id,
            "type": schedule_type,
            "run_time": run_time,
            "sources": sources,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        # TODO: Implement actual scheduling logic
        # This could use APScheduler, Celery, or similar
        
        return schedule_id
UPLOADS_TABLE_NAME = "uploads"
logging.basicConfig(level=logging.INFO)

# =========================================================================
# 🔥 JSON SAFETY HELPER FUNCTION - SIMPLIFIED 🔥
# =========================================================================

def make_json_safe(obj):
    """Convert any object to JSON-safe Python types - SIMPLIFIED"""
    if obj is None:
        return None
    
    # Check for NaN/NaT
    try:
        if pd.isna(obj):
            return None
    except:
        pass
    
    # Handle dict
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    
    # Handle list
    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    
    # Handle basic types
    if isinstance(obj, (str, int, bool, float)):
        return obj
    
    # Convert numpy types
    if isinstance(obj, np.integer):
        return int(obj)
    
    if isinstance(obj, np.floating):
        try:
            if np.isfinite(obj):
                return float(obj)
            else:
                return None
        except:
            return None
    
    # Handle numpy scalar
    if isinstance(obj, np.generic):
        try:
            return obj.item()
        except:
            return None
    
    # Handle datetime/timestamp
    if isinstance(obj, (pd.Timestamp, datetime)):
        try:
            return str(obj)
        except:
            return None
    
    # Everything else: convert to string
    try:
        return str(obj)
    except:
        return None

# =========================================================================
# ⭐️ 1. ANALYTICS: get_filtered_data - SIMPLIFIED
# =========================================================================

async def get_filtered_data(filters: DataFilter, user_id: str) -> List[Dict[str, Any]]:
    admin_client: Client = get_supabase_service()

    try:
        # Ensure comparison value is a string UUID
        user_uuid = str(uuid.UUID(user_id))

        # ---- Build metadata query ----
        query = (
            admin_client
            .table(UPLOADS_TABLE_NAME)
            .select("table_name")
            .eq("user_id", user_uuid)
        )

        if filters.table_names:
            query = query.in_("table_name", filters.table_names)

        metadata_response = query.execute()

        if not metadata_response.data:
            return []

        table_names = [row["table_name"] for row in metadata_response.data]

        # ---- Build results from each table ----
        all_results = []
        
        for table_name in table_names:
            try:
                # Query each table directly
                response = admin_client.table(table_name)\
                    .select("id, user_id, row_data")\
                    .eq("user_id", user_uuid)\
                    .limit(filters.limit)\
                    .execute()
                
                # Extract and flatten data
                for item in response.data:
                    if 'row_data' in item and isinstance(item['row_data'], dict):
                        row = item['row_data'].copy()
                        row['_source_table'] = table_name
                        row['_record_id'] = item.get('id')
                        all_results.append(row)
                    else:
                        item['_source_table'] = table_name
                        all_results.append(item)
                        
            except Exception as table_err:
                logging.warning(f"Error querying table {table_name}: {table_err}")
                continue
        
        # Apply offset
        start_idx = min(filters.offset, len(all_results))
        end_idx = min(filters.offset + filters.limit, len(all_results))
        
        return all_results[start_idx:end_idx]

    except Exception as e:
        logging.error(f"Analytics query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics data")

# =========================================================================
# ⭐️ 2. DATA PREVIEW: fetch_table_data_rows - FIXED VERSION
# =========================================================================

async def fetch_table_data_rows(upload_id: str, user_id: str, limit: int) -> List[Dict[str, Any]]:
    admin_client: Client = get_supabase_service()

    try:
        # Ensure comparison value is a string UUID
        user_uuid = str(uuid.UUID(user_id))

        # ---- Fetch table name ----
        metadata_response = (
            admin_client
            .table(UPLOADS_TABLE_NAME)
            .select("table_name")
            .eq("id", upload_id)
            .eq("user_id", user_uuid)
            .maybe_single()
            .execute()
        )

        if not metadata_response.data:
            raise HTTPException(
                status_code=404, 
                detail=f"Dataset not found for upload_id: {upload_id}, user_id: {user_uuid}"
            )

        table_name = metadata_response.data["table_name"]
        
        logging.info(f"Fetching data from table: {table_name}")

        # ---- Use Supabase client directly ----
        response = admin_client.table(table_name)\
            .select("id, user_id, row_data")\
            .eq("user_id", user_uuid)\
            .limit(limit)\
            .execute()
        
        logging.info(f"Query returned {len(response.data) if response.data else 0} rows")
        
        # ----- CRITICAL FIX: Extract and flatten row_data -----
        flattened_data = []
        for item in response.data:
            if 'row_data' in item and isinstance(item['row_data'], dict):
                # Extract the actual data from row_data
                row = item['row_data'].copy()
                # Keep metadata if needed (optional)
                row['_record_id'] = item.get('id')
                row['_user_id'] = item.get('user_id')
                flattened_data.append(row)
            else:
                # If no row_data, use item as-is
                flattened_data.append(item)
        
        return flattened_data

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(ve)}")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Preview fetch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch preview data: {str(e)}"
        )

# =========================================================================
# ⭐️ 3. CORE ETL: process_and_store_data - OPTIMIZED VERSION
# =========================================================================

async def process_and_store_data(
    file_content: bytes,
    filename: str,
    user_id: str
) -> Dict[str, Any]:

    upload_uuid = str(uuid.uuid4())
    table_safe_id = upload_uuid.replace("-", "_")
    data_table_name = f"data_{table_safe_id}"

    # ------------------ EXTRACT ------------------
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(file_content))
        elif filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(BytesIO(file_content), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File read failed: {e}")

    # ------------------ TRANSFORM ------------------
    original_rows = len(df)
    
    # Remove completely empty rows
    df.dropna(how="all", inplace=True)
    
    # Replace all NaN/NaT with None
    df = df.replace({np.nan: None, pd.NaT: None})
    
    # Convert datetime columns to string
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
    
    cleaned_rows = len(df)
    
    # Convert to records early to check data
    records = df.to_dict("records")
    
    if not records:
        raise HTTPException(status_code=400, detail="No data found in file after cleaning")

    admin_client: Client = get_supabase_service()
    user_uuid = str(uuid.UUID(user_id))

    try:
        # ------------------ LOAD: Create table ------------------
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS "{data_table_name}" (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
                row_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """
        
        logging.info(f"Creating table: {data_table_name}")
        
        try:
            # Try exec_sql first
            admin_client.rpc(
                "exec_sql",
                {"sql_text": create_table_sql}
            ).execute()
            logging.info(f"✓ Table created via exec_sql: {data_table_name}")
        except Exception as create_err:
            logging.error(f"exec_sql failed: {create_err}")
            
            # Try create_unique_data_table as fallback
            try:
                admin_client.rpc(
                    "create_unique_data_table",
                    {
                        "table_name": data_table_name,
                        "owner_id": user_uuid
                    }
                ).execute()
                logging.info(f"✓ Table created via create_unique_data_table: {data_table_name}")
            except Exception as rpc_err:
                logging.error(f"RPC also failed: {rpc_err}")
                
                # Check if table already exists
                try:
                    check_sql = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{data_table_name}');"
                    check_result = admin_client.rpc("execute_sql", {"sql": check_sql}).execute()
                    if check_result.data and check_result.data[0].get('exists'):
                        logging.info(f"Table already exists: {data_table_name}")
                    else:
                        raise HTTPException(status_code=500, detail=f"Failed to create table: {str(create_err)}")
                except:
                    raise HTTPException(status_code=500, detail=f"Failed to create table: {str(create_err)}")
        
        # ------------------ Wait for schema cache refresh ------------------
        logging.info("Waiting for schema cache refresh...")
        time.sleep(2)
        
        # ------------------ LOAD: Insert rows ------------------
        insert_rows = []
        for i, record in enumerate(records):
            cleaned_record = make_json_safe(record)
            
            if not isinstance(cleaned_record, dict):
                logging.warning(f"Skipping record {i}: not a dictionary")
                continue
            
            insert_rows.append({
                "user_id": user_uuid, 
                "row_data": cleaned_record
            })
        
        if not insert_rows:
            raise HTTPException(status_code=400, detail="No valid data to insert")

        # Insert data in batches
        inserted_count = 0
        batch_size = 50
        
        for i in range(0, len(insert_rows), batch_size):
            batch = insert_rows[i:i + batch_size]
            try:
                response = admin_client.table(data_table_name).insert(batch).execute()
                inserted_count += len(response.data) if response.data else 0
                logging.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} rows")
            except Exception as batch_err:
                logging.error(f"Batch {i//batch_size + 1} failed: {batch_err}")
                
                # Try individual inserts as fallback
                for single_row in batch:
                    try:
                        admin_client.table(data_table_name).insert(single_row).execute()
                        inserted_count += 1
                    except Exception as single_err:
                        logging.error(f"Single row insert failed: {single_err}")

        if inserted_count == 0:
            raise HTTPException(status_code=500, detail="No rows were successfully inserted")

        # ------------------ LOAD: Metadata ------------------
        metadata = {
            "id": upload_uuid,
            "user_id": user_uuid,
            "filename": filename,
            "table_name": data_table_name,
            "uploaded_at": datetime.utcnow().isoformat(),
            "rows": cleaned_rows
        }

        admin_client.table(UPLOADS_TABLE_NAME).insert(metadata).execute()
        logging.info(f"✓ Metadata saved: {upload_uuid}")

        return {
            "status": "success",
            "upload_id": upload_uuid,
            "table_name": data_table_name,
            "original_rows": original_rows,
            "cleaned_rows": cleaned_rows,
            "inserted_rows": inserted_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"ETL failed: {e}", exc_info=True)
        
        # Cleanup on failure
        try:
            drop_sql = f'DROP TABLE IF EXISTS "{data_table_name}" CASCADE;'
            admin_client.rpc("exec_sql", {"sql_text": drop_sql}).execute()
            logging.info(f"Cleaned up table: {data_table_name}")
        except Exception as cleanup_err:
            logging.warning(f"Failed to cleanup table: {cleanup_err}")
        
        raise HTTPException(status_code=500, detail=f"ETL processing failed: {str(e)}")