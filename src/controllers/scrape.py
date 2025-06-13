from src.utils.scrape import get_job_postings
from loguru import logger
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename
from src.services.supabase import get_all_open_role_audit_tasks, get_last_scrape_broadcast, get_new_jobs_to_send_out, update_config_last_updated_time

from src.controllers.audit import start_open_role_audit
from src.services.cloud_tasks import create_task
import asyncio
from datetime import datetime
import requests
from fastapi import HTTPException

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
        last_broadcast_time = await get_last_scrape_broadcast()
        if not last_broadcast_time:
            raise HTTPException(status_code=404, detail="No scrape broadcast date found")
        
        # Convert the string timestamp to datetime object
        last_broadcast_date = datetime.fromisoformat(last_broadcast_time.replace('Z', '+00:00'))
        already_ran_today = last_broadcast_date.date() >= datetime.now().date()
        
        if already_ran_today:
            return {
                "message": "Scrape broadcast already ran today",
                "payload": {
                    "lastBroadcastDate": last_broadcast_date
                }
            }
        
        
        tasks = await get_all_open_role_audit_tasks()
        
        all_tasks_ran_today = all(
            datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00')).date() >= datetime.now().date() and task["status"] in ["completed", "failed"]
            for task in tasks
        )
        
        if not all_tasks_ran_today:
            return {
                "message": "Today's scraping tasks have not completed yet",
                "payload": {
                    "lastBroadcastDate": last_broadcast_date
                }
            }
        

        # Send out internal email with new job postings
        # generate apm payload: internshipEmailData, fullTimeEmailData
        # call directus endpoint
        new_apm_jobs = await get_new_jobs_to_send_out("apm")
        new_consulting_jobs = await get_new_jobs_to_send_out("consulting")
        
        apm = {
            "internshipData": [job for job in new_apm_jobs if job["jobType"] == "internship"],
            "fullTimeData": [job for job in new_apm_jobs if job["jobType"] == "full-time"],
            "site": "apm"
        }
        
        consulting = {
            "internshipData": [job for job in new_consulting_jobs if job["jobType"] == "internship"],
            "fullTimeData": [job for job in new_consulting_jobs if job["jobType"] == "full-time"],
            "site": "consulting"
        }
        
        if len(apm["internshipData"]) > 0 or len(apm["fullTimeData"]) > 0:
            # # Send email with new job postings via Directus flow
            response = requests.post(
                "https://directus.apmseason.com/flows/trigger/28537cec-ec71-43b0-b78c-295c9181b2c5",
                json=apm
            )
        if response.status_code != 200:
            logger.error(f"Error sending email: {response.text}")
            raise Exception("Failed to send email with new job postings")
        
        if len(consulting["internshipData"]) > 0 or len(consulting["fullTimeData"]) > 0:
            response = requests.post(
                "https://directus.apmseason.com/flows/trigger/28537cec-ec71-43b0-b78c-295c9181b2c5",
                json=consulting
            )
        
        if response.status_code != 200:
            logger.error(f"Error sending email: {response.text}")
            raise Exception("Failed to send email with new job postings")
        
        await update_config_last_updated_time()
        
        return {
            "message": "Email sent successfully",
            "payload": {
                "apm": apm,
                "consulting": consulting
            }
        }
         
    except Exception as e:
        logger.error(f"Error getting scrape status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    