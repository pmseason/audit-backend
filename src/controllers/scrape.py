from src.utils.scrape import get_job_postings
from loguru import logger
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename
from src.services.supabase import get_all_open_role_audit_tasks, get_last_scrape_broadcast, get_new_jobs_to_send_out

from src.controllers.audit import start_open_role_audit
from src.services.cloud_tasks import create_task
import asyncio
from datetime import datetime
import requests

async def start_scrape_roles():
    # fetch open role audit tasks
    tasks = await get_all_open_role_audit_tasks()
    # Create a cloud task for each audit task
    task_promises = [
        create_task({
            "type": "OPEN_ROLE_AUDIT",
            "taskId": task["id"],
        })
        for task in tasks
    ]
        
    await asyncio.gather(*task_promises)
    return {
        "message": "Scrape tasks started successfully",
    }

async def post_scrape_results_controller():
    """
    Get the current status of scrape tasks
    Returns a dictionary containing status information
    """
    try:
        last_updated_time = await get_last_scrape_broadcast()
        if not last_updated_time:
            return {
                "status": "error",
                "message": "No scrape broadcast date found"
            }
        
        # Convert the string timestamp to datetime object
        last_updated_date = datetime.fromisoformat(last_updated_time.replace('Z', '+00:00'))
        already_ran_today = last_updated_date.date() >= datetime.now().date()
        
        tasks = await get_all_open_role_audit_tasks()
        
        all_tasks_ran = all(
            datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00')).date() >= datetime.now().date()
            for task in tasks
        )
        
        if not already_ran_today and all_tasks_ran:
            # Send out internal email with new job postings
            # generate apm payload: internshipEmailData, fullTimeEmailData
            # call directus endpoint
            new_apm_jobs = await get_new_jobs_to_send_out("apm")
            new_consulting_jobs = await get_new_jobs_to_send_out("consulting")
            
            apm = {
                "internshipData": [job for job in new_apm_jobs if job["jobType"] == "internship"],
                "fullTimeData": [job for job in new_apm_jobs if job["jobType"] == "full-time"]
            }
            
            consulting = {
                "internshipData": [job for job in new_consulting_jobs if job["jobType"] == "internship"],
                "fullTimeData": [job for job in new_consulting_jobs if job["jobType"] == "full-time"]
            }
            
            payload = {
                "apm": apm,
                "consulting": consulting
            }
            # Send email with new job postings via Directus flow
            response = requests.post(
                "https://directus.apmseason.com/flows/trigger/28537cec-ec71-43b0-b78c-295c9181b2c5",
                json=payload
            )
            if response.status_code != 200:
                logger.error(f"Error sending email: {response.text}")
                raise Exception("Failed to send email with new job postings")
            
            return {
                "message": "Email sent successfully"
            }
        
        return {
           "message": "No new jobs to send out"
        }
         
    except Exception as e:
        logger.error(f"Error getting scrape status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    