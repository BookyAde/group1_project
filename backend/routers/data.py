# backend/routers/data.py (FINALIZED UPLOAD FIX WITH DEBUGGING)

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Dict, Any, List
from supabase import Client
import logging 
import traceback

# Imports for dependencies. The security imports are commented out for bypass.
from backend.core.config import get_supabase_service
# from backend.core.security import get_current_user, User 
from backend.services.etl import (
    process_and_store_data, 
    fetch_table_data_rows 
)

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)

# FIXED, KNOWN UUID FOR BYPASS
BYPASS_USER_ID = "11111111-1111-1111-1111-111111111111"
UPLOADS_TABLE_NAME = "uploads"


# ----------------------------------------------------------------------------------
# ENDPOINT 1: /upload (File Upload - Authentication Removed)
# ----------------------------------------------------------------------------------

@router.post("/upload", status_code=status.HTTP_200_OK) 
async def upload_file(
    file: UploadFile = File(...),
    # Removed: current_user: User = Depends(get_current_user),
):
    """Upload and process CSV/Excel files"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.xls', '.xlsx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV and Excel files are supported"
            )
        
        # Read file content as bytes
        file_content = await file.read() 
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        logging.info(f"Processing file: {file.filename}, size: {len(file_content)} bytes")
        
        # ⭐️ FIX: Pass the three arguments matching the service signature ⭐️
        upload_metadata = await process_and_store_data(
            file_content=file_content, 
            filename=file.filename, 
            user_id=BYPASS_USER_ID # Fixed UUID
        )
        
        return {
            "message": "File uploaded and processed successfully", 
            "metadata": upload_metadata,
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(file_content)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error("ETL FAILED AT LOAD STAGE")
        logging.error(f"Error: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )

# ----------------------------------------------------------------------------------
# ENDPOINT 2: /list (List all datasets)
# ----------------------------------------------------------------------------------

@router.get("/list")
async def list_datasets(
    supabase: Client = Depends(get_supabase_service)
):
    """List ALL unique datasets (metadata from 'uploads' table) without user filtering."""
    try:
        response = supabase.table(UPLOADS_TABLE_NAME)\
            .select("id, filename, table_name, uploaded_at, rows, user_id")\
            .order("uploaded_at", desc=True)\
            .execute()
        
        return {
            "count": len(response.data),
            "datasets": response.data
        }
    except Exception as e:
        logging.error(f"Failed to list datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------------
# ENDPOINT 3: /file/{upload_id} (Get file data preview)
# ----------------------------------------------------------------------------------

@router.get("/file/{upload_id}", response_model=List[Dict[str, Any]])
async def get_file_data(
    upload_id: str,
    limit: int = 100,
):
    """
    Fetches N rows of raw data content, passing the fixed BYPASS_USER_ID.
    """
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Limit cannot exceed 1000 rows for preview."
        )
        
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be positive"
        )
        
    try:
        data = await fetch_table_data_rows(
            upload_id=upload_id, 
            user_id=BYPASS_USER_ID, # <--- FIXED UUID ID
            limit=limit
        )
        return data or []
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching data preview for {upload_id}: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve data preview."
        )

# ----------------------------------------------------------------------------------
# ENDPOINT 4: /status/{task_id} (Task status - dummy)
# ----------------------------------------------------------------------------------

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Return a successful dummy status for quick defense."""
    return {
        "task_id": task_id, 
        "status": "SUCCESS", 
        "message": "Task completion assumed for defense mode."
    }

# ----------------------------------------------------------------------------------
# NEW DEBUG ENDPOINTS (Add these for troubleshooting)
# ----------------------------------------------------------------------------------

@router.post("/test-upload")
async def test_upload(
    file: UploadFile = File(...),
    supabase: Client = Depends(get_supabase_service)
):
    """Debug endpoint to test upload without full ETL"""
    try:
        content = await file.read()
        
        # Just test reading the file
        import pandas as pd
        from io import BytesIO
        
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content), engine='openpyxl')
        
        # Test JSON conversion on first row
        first_row = df.iloc[0].to_dict()
        
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "first_row": first_row,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
    except Exception as e:
        logging.error(f"Test upload failed: {e}")
        raise HTTPException(status_code=400, detail=f"Test failed: {str(e)}")

@router.get("/test-supabase-connection")
async def test_supabase_connection(
    supabase: Client = Depends(get_supabase_service)
):
    """Test Supabase connection"""
    try:
        # Test simple query
        result = supabase.table(UPLOADS_TABLE_NAME)\
            .select("count", count="exact")\
            .execute()
        
        return {
            "connected": True,
            "uploads_count": result.count,
            "supabase_url": supabase.supabase_url if hasattr(supabase, 'supabase_url') else "Unknown"
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

@router.delete("/cleanup-test-data")
async def cleanup_test_data(
    supabase: Client = Depends(get_supabase_service)
):
    """Cleanup test data (use with caution)"""
    try:
        # Find and delete test tables
        response = supabase.table(UPLOADS_TABLE_NAME)\
            .select("table_name")\
            .eq("user_id", BYPASS_USER_ID)\
            .execute()
        
        deleted_tables = []
        for upload in response.data:
            table_name = upload["table_name"]
            try:
                # Drop the data table
                supabase.rpc(
                    "drop_unique_data_table",
                    {"table_name": table_name}
                ).execute()
                deleted_tables.append(table_name)
            except Exception as e:
                logging.warning(f"Failed to drop table {table_name}: {e}")
        
        # Delete metadata
        delete_response = supabase.table(UPLOADS_TABLE_NAME)\
            .delete()\
            .eq("user_id", BYPASS_USER_ID)\
            .execute()
        
        return {
            "deleted_metadata": len(delete_response.data),
            "deleted_tables": deleted_tables,
            "message": f"Cleaned up {len(deleted_tables)} tables for test user"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")