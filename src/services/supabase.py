from supabase import create_client, Client
from typing import List, Optional
import os
from enum import Enum
from loguru import logger
from postgrest.exceptions import APIError
from src.types.audit import AuditStatus

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
        "status": AuditStatus.NOT_RUN,
        "statusMessage": "Task has not run"
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
            .select("*, job(*, company(*, logo(*)))") \
            .execute()
            
        return response.data
    except APIError as e:
        raise Exception(f"Error fetching all closed role audit tasks: {str(e)}")

async def update_closed_role_task_status(task_ids: List[str], status: AuditStatus, status_message: str, additional_payload: dict = None):
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

async def get_all_open_role_audit_tasks():
    """Fetch all open role audit tasks."""
    try:
        response_1 = supabase.table("open_role_audit_tasks") \
            .select("*") \
            .execute()
            
        tasks = response_1.data
        
        response_2 = supabase.table("scraped_jobs") \
            .select("*") \
            .in_("task", [task["id"] for task in tasks]) \
            .execute()
            
        scraped_jobs = response_2.data
        
        for task in tasks:
            task["scraped_jobs"] = [scraped_job for scraped_job in scraped_jobs if scraped_job["task"] == task["id"]]
            
        return tasks
        
    except APIError as e:
        raise Exception(f"Error fetching all open role audit tasks: {str(e)}")

async def insert_open_role_audit_task(url: str, extra_notes: str = None):
    """Insert a new open role audit task."""
    task = {
        "url": url,
        "status": AuditStatus.NOT_RUN,
        "status_message": "Task has not run",
        "extra_notes": extra_notes
    }
    
    try:
        response = supabase.table("open_role_audit_tasks") \
            .insert(task) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error inserting open role audit task: {str(e)}")


async def get_open_role_audit_tasks_by_ids(task_ids: List[str]):
    """Fetch open role audit tasks by their IDs."""
    try:
        response = supabase.table("open_role_audit_tasks") \
            .select("*") \
            .in_("id", task_ids) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error fetching open role audit tasks by IDs: {str(e)}")
    
    
async def update_open_role_task_status(task_ids: List[str], status: AuditStatus, status_message: str, extra_data: dict = None):
    """Update status and related fields for open role audit tasks.
    
    Args:
        task_ids: List of task IDs to update
        status: New AuditStatus value
        status_message: Status message to set
        extra_data: Optional dict of additional fields to update
    """
    try:
        update_data = {
            "status": status,
            "status_message": status_message
        }
        
        if extra_data:
            update_data.update(extra_data)
            
        response = supabase.table("open_role_audit_tasks") \
            .update(update_data) \
            .in_("id", task_ids) \
            .execute()
            
        return response.data
    except APIError as e:
        raise Exception(f"Error updating task status: {str(e)}")

async def insert_scraped_jobs(jobs: List[dict], task_id: int):
    """Insert scraped jobs for a specific task."""
    try:
        jobs_with_task = [{**job, "task": task_id} for job in jobs]
        
        response = supabase.table("scraped_jobs") \
            .insert(jobs_with_task) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error inserting scraped jobs: {str(e)}")

async def delete_open_role_audit_task(task_id: int):
    """Delete an open role audit task by its ID."""
    try:
        response = supabase.table("open_role_audit_tasks") \
            .delete() \
            .eq("id", task_id) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error deleting open role audit task: {str(e)}")
    
    
async def get_companies_with_career_page_urls():
    """Get all companies that have career page URLs defined.
    
    Returns:
        List of company records with non-null career_page_link fields
    """
    try:
        response = supabase.table("companies") \
            .select("*") \
            .neq("career_page_link", None) \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error fetching companies: {str(e)}")