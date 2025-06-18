from supabase import create_client, Client
from typing import List, Optional
import os
from enum import Enum
from loguru import logger
from postgrest.exceptions import APIError
from src.types.audit import AuditStatus
from datetime import datetime

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(supabase_url, supabase_key)


async def upload_screenshot_to_storage(screenshot: bytes, filename: str) -> str:
    """
    Upload a base64 encoded screenshot to Supabase storage.
    
    Args:
        screenshot_base64 (str): Base64 encoded screenshot data
        filename (str): Name to save the file as
        
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        # Remove base64 prefix if present
        # Upload to screenshots bucket
        response = supabase.storage.from_("audit").upload(
            path=filename,
            file=screenshot,
            file_options={"contentType": "image/png", "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_("audit").get_public_url(filename)
        return public_url
        
    except Exception as e:
        logger.error(f"Error uploading screenshot to storage: {str(e)}")
        raise Exception(f"Failed to upload screenshot: {str(e)}")


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

###### OPEN ROLE AUDIT ##########################

async def get_all_open_role_audit_tasks():
    """Fetch all open role audit tasks."""
    try:
        response = supabase.table("open_role_audit_tasks") \
            .select("*, company(*, logo(filename_disk))") \
            .execute()
            
        return response.data
        
    except APIError as e:
        raise Exception(f"Error fetching all open role audit tasks: {str(e)}")

async def insert_open_role_audit_task(url: str):
    """Insert a new open role audit task."""
    task = {
        "url": url,
        "status": AuditStatus.NOT_RUN,
        "status_message": "Task has not run"
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
            "status_message": status_message,
            "updated_at": datetime.now().isoformat().replace('Z', '+00:00')
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

###### SCRAPED JOBS ##########################
async def insert_scraped_jobs(jobs: List[dict]):
    """Insert scraped jobs for a specific task."""
    try:
        response = supabase.table("scraped_positions") \
            .insert(jobs) \
            .execute()
        return response.data
    except APIError as e:
        logger.error(f"Error inserting scraped jobs: {str(e)}")

async def filter_jobs_to_scrape(urls: List[str]):
    """Filter jobs to scrape by urls that do not exist in the db"""
    try:
        
        response = supabase.table("scraped_positions") \
            .select("*") \
            .in_("url", urls) \
            .execute()
        
        already_scraped_urls = [job["url"] for job in response.data]
        
        return [url for url in urls if url not in already_scraped_urls]
    except APIError as e:
        raise Exception(f"Error filtering jobs to scrape: {str(e)}")
    
###### SCRAPE BROADCAST ##########################

async def get_last_scrape_broadcast():
    """Get the last scrape broadcast date."""
    try:
        response = supabase.table("config") \
            .select("lastUpdatedTime") \
            .eq("id", "scraping_automation") \
            .limit(1) \
            .execute()
        return response.data[0]["lastUpdatedTime"]
    except APIError as e:
        raise Exception(f"Error getting last scrape broadcast: {str(e)}")
    

def get_date_added_text(date_added: str) -> str:
    """Transform date added into a human readable format."""
    now = datetime.now()
    time = now.timestamp() - datetime.fromisoformat(date_added.replace('Z', '+00:00')).timestamp()
    difference_in_days = int(time / (60 * 60 * 24))

    if difference_in_days == 0:
        return "Added Today"
    elif difference_in_days == 1:
        return "Added 1 Day Ago"
    elif 1 < difference_in_days <= 30:
        return f"Added {difference_in_days} Days Ago"
    else:
        return "Added 30+ Days Ago"

def get_visa_text(visa: str) -> str:
    """Transform visa status into a formatted string."""
    if visa == "yes":
        return "Visa Sponsored &#9745;"
    elif visa == "no":
        return "Visa Sponsored &#9746;"
    else:
        return "Visa Sponsored ?"

async def get_new_jobs_to_send_out(site: str):
    """Get the new jobs to send out with transformed data structure."""
    try:
        response = supabase.table("scraped_positions") \
            .select("*, company(*, logo(*))") \
            .eq("status", "open") \
            .eq("site", site) \
            .not_.is_("title", None) \
            .gte("createdAt", datetime.now().date().isoformat()) \
            .execute()
            
        transformed_positions = []
        for position in response.data:
            company = position.get('company', {})
            logo = company.get('logo', {})
            
            transformed_position = {
                'companyName': company.get('name'),
                'logoUrl': f"https://images.careerseason.com/{logo.get('filename_disk')}" if logo.get('filename_disk') else None,
                'title': position.get('title'),
                'url': position.get('url'),
                'dateAddedText': get_date_added_text(position.get('createdAt', datetime.now().isoformat())),
            }
            if position.get('salaryText'):
                transformed_position['salaryText'] = position.get('salaryText')
            if position.get('jobType'):
                transformed_position['jobType'] = position.get('jobType')
            if position.get('visaSponsored'):
                transformed_position['visaText'] = get_visa_text(position.get('visaSponsored'))
            
            transformed_positions.append(transformed_position)
            
        return transformed_positions[:10]
    except APIError as e:
        raise Exception(f"Error getting new jobs to send out: {str(e)}")

async def update_config_last_updated_time():
    """Update the last updated time for the config table."""
    try:
        response = supabase.table("config") \
            .update({"lastUpdatedTime": datetime.now().isoformat().replace('Z', '+00:00')}) \
            .eq("id", "scraping_automation") \
            .execute()
        return response.data
    except APIError as e:
        raise Exception(f"Error updating config last updated time: {str(e)}")