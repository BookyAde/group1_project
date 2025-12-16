# 📄 backend/services/background.py (COMPLETE AND CORRECT VERSION)

import asyncio
# CRITICAL: This line imports the function that was reported as undefined.
from backend.services.etl import process_and_store_data 
from backend.core.config import supabase_service 
from typing import Dict, Any

# Table to track the status of long-running tasks
TASK_STATUS_TABLE = "etl_tasks"

async def log_task_status(task_id: str, status: str, result: Dict[str, Any] = None):
    """
    Logs the status of a background task to a specific Supabase table.
    """
    # Ensure the supabase_service client is ready
    if supabase_service is None:
        print(f"WARNING: Supabase service client not initialized. Cannot log task status for {task_id}.")
        return

    try:
        data = {"id": task_id, "status": status, "result": result, "user_id": result.get("user_id")}
        
        # Use service key to bypass RLS and ensure the log always succeeds
        supabase_service.table(TASK_STATUS_TABLE).upsert(data, on_conflict="id").execute()
    except Exception as e:
        print(f"ERROR: Failed to log task status for {task_id}: {e}")

async def run_etl_in_background(task_id: str, file_content: bytes, filename: str, user_id: str):
    """
    The main asynchronous worker function.
    """
    # Log PENDING status before starting (optional, but good practice)
    await log_task_status(task_id, "PENDING", {"user_id": user_id}) 

    await log_task_status(task_id, "RUNNING", {"user_id": user_id})
    
    # Simulate a long-running process 
    # await asyncio.sleep(2) # You can keep this for testing, but remove for production
    
    try:
        # Call the actual business logic from the ETL service (which is now imported)
        result = await process_and_store_data(file_content, filename, user_id)
        
        # Add user_id to the result dict for consistent logging
        result["user_id"] = user_id 
        
        if result.get("status") == "success":
            await log_task_status(task_id, "COMPLETED", result)
        else:
            await log_task_status(task_id, "FAILED", result)
            
    except Exception as e:
        await log_task_status(task_id, "FAILED", {"message": f"Critical task error: {e}", "user_id": user_id})