from src.utils.scrape import get_job_postings
from loguru import logger
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename
from src.services.supabase import get_all_open_role_audit_tasks
from src.controllers.audit import start_open_role_audit
from src.services.cloud_tasks import create_task
import asyncio

async def start_scrape_roles():
    # fetch open role audit tasks
    tasks = await get_all_open_role_audit_tasks()
    # Create a cloud task for each audit task
    task_promises = [
        create_task({
            "type": "OPEN_ROLE_AUDIT",
            "taskId": task["id"],
            "url": task["url"],
            "extra_notes": task["extra_notes"],
            "site": task["site"]
        })
        for task in tasks
    ]
        
    await asyncio.gather(*task_promises)