from typing import List
from fastapi import HTTPException
from loguru import logger
from ..services.supabase import (
    clear_closed_role_audit_tasks,
    get_open_jobs,
    insert_closed_role_audit_tasks,
    get_closed_role_audit_tasks_by_ids,
    get_all_closed_role_audit_tasks,
    update_task_status
)
from ..services.cloud_tasks import create_task
from ..types.audit import AuditStatus
import asyncio

async def create_closed_role_audit():
    try:
        jobs = await get_open_jobs()
        logger.info(f"Found {len(jobs)} open jobs")
        await clear_closed_role_audit_tasks()
        
        # Extract job IDs and create audit tasks (default status is NOT_RUN)
        job_ids = [job['id'] for job in jobs]
        await insert_closed_role_audit_tasks(job_ids)
        
        return {"message": "Closed role audit created successfully", "jobs": jobs}
    except Exception as error:
        print(f"Error creating closed role audit: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_closed_role_audit(task_ids: List[str]):
    try:
        if not isinstance(task_ids, list):
            raise HTTPException(status_code=400, detail="taskIds must be an array")

        tasks = await get_closed_role_audit_tasks_by_ids(task_ids)

        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found with the provided IDs")

        # Update task status to PENDING
        await update_task_status(task_ids, AuditStatus.PENDING, "Task is pending", {"justification": "", "result": "", "screenshot": ""})
        
        # Create a cloud task for each audit task
        task_promises = [
            create_task({
                "type": "CLOSED_ROLE_AUDIT",
                "jobId": task["job"]["id"],
                "taskId": task["id"],
                "url": task["job"]["url"]
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

async def get_closed_role_audit_tasks():
    try:
        tasks = await get_all_closed_role_audit_tasks()
        return tasks
    except Exception as error:
        print(f"Error fetching closed role audit tasks: {error}")
        raise HTTPException(status_code=500, detail="Internal server error") 