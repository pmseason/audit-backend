from typing import List, Optional
from fastapi import HTTPException
from loguru import logger
from ..services.supabase import (
    clear_closed_role_audit_tasks,
    get_open_jobs,
    insert_closed_role_audit_tasks,
    get_closed_role_audit_tasks_by_ids,
    get_all_closed_role_audit_tasks,
    get_all_open_role_audit_tasks,
    insert_open_role_audit_task,
    update_closed_role_task_status,
    get_open_role_audit_tasks_by_ids,
    update_open_role_task_status,
    delete_open_role_audit_task
)
from ..services.cloud_tasks import create_task
from ..types.audit import AuditStatus
import asyncio
from src.utils.scrape import get_job_postings
from loguru import logger
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename
from src.services.supabase import get_all_open_role_audit_tasks, get_last_scrape_broadcast, get_new_jobs_to_send_out, update_config_last_updated_time
import requests
from datetime import datetime

async def start_closed_role_audit():
    try:
        jobs = await get_open_jobs()
        logger.info(f"Found {len(jobs)} open jobs")
        await clear_closed_role_audit_tasks()
        
        # Extract job IDs and create audit tasks (default status is NOT_RUN)
        job_ids = [job['id'] for job in jobs]
        await insert_closed_role_audit_tasks(job_ids)

        tasks = await get_all_closed_role_audit_tasks()
        
        # Create a cloud task for each audit task
        task_promises = [
            create_task({
                "type": "CLOSED_ROLE_AUDIT",
                "taskId": task["id"],
            })
            for task in tasks
        ]
        
        await asyncio.gather(*task_promises)
        
        return {
            "message": "Closed role audit started successfully",
            "tasksCount": len(tasks)
        }
    except HTTPException:
        raise
    except Exception as error:
        print(f"Error starting closed role audit: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def start_open_role_audit():
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
