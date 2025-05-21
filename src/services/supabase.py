from supabase import create_client, Client
from typing import List, Optional
import os
from enum import Enum
from loguru import logger
from postgrest.exceptions import APIError

class AuditStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

async def get_open_jobs():
    """Fetch all open jobs from the positions table."""
    logger.info("Fetching open jobs")
    try:
        response = supabase.table("positions").select("*, companies(*)").eq("status", "open").eq("hidden", False).execute()
        return response.data or []
    except APIError as e:
        raise Exception(f"Error fetching open jobs: {str(e)}")

async def clear_closed_role_audit_tasks():
    """Clear all closed role audit tasks."""
    try:
        response = supabase.table("closed_role_audit_tasks") \
            .delete() \
            .neq("id", 0) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error clearing closed role audit tasks: {str(e)}")

async def insert_closed_role_audit_tasks(job_ids: List[str]):
    """Insert new closed role audit tasks for given job IDs."""
    tasks = [{
        "job": job_id,
        "status": AuditStatus.PENDING,
        "statusMessage": "Task is pending"
    } for job_id in job_ids]
    
    try:
        response = supabase.table("closed_role_audit_tasks") \
            .insert(tasks) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error inserting closed role audit tasks: {str(e)}")

async def get_closed_role_audit_tasks_by_ids(task_ids: List[str]):
    """Fetch specific closed role audit tasks by their IDs."""
    try:
        response = supabase.table("closed_role_audit_tasks") \
            .select("*, job(*, company(*))") \
            .in_("id", task_ids) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error fetching tasks: {str(e)}")

async def get_all_closed_role_audit_tasks():
    """Fetch all closed role audit tasks."""
    try:
        response = supabase.table("closed_role_audit_tasks") \
            .select("*, job(*, company(*))") \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error fetching all closed role audit tasks: {str(e)}")

async def update_task_status(task_ids: List[str], status: AuditStatus, status_message: str, additional_payload: dict = None):
    """
    Update task status and optionally additional fields for specific tasks.
    
    Args:
        task_ids: List of task IDs to update
        status: AuditStatus enum value
        status_message: Status message string
        additional_payload: Optional dictionary containing additional fields to update (e.g. result, justification, screenshot)
    """
    try:
        payload = {
            "status": status,
            "statusMessage": status_message
        }
        
        if additional_payload:
            payload.update(additional_payload)
            
        response = supabase.table("closed_role_audit_tasks") \
            .update(payload) \
            .in_("id", task_ids) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error updating task status: {str(e)}")

# async def insert_audit_results(task_id: str, result: str, justification: str, screenshot: str):
#     """Insert audit results for a specific task."""
#     try:
#         response = supabase.table("closed_role_audit_tasks") \
#             .update({
#                 "result": result,
#                 "justification": justification,
#                 "screenshot": screenshot
#             }) \
#             .eq("id", task_id) \
#             .execute()
#         return response.data
#     except APIError as e:
#         raise Exception(f"Error updating audit results: {str(e)}")
