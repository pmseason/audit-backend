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
        await update_closed_role_task_status(task_ids, AuditStatus.PENDING, "Task is pending", {"justification": "", "result": "", "screenshot": ""})
        
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

async def get_open_role_audit_tasks():
    try:
        tasks = await get_all_open_role_audit_tasks()
        return tasks
    except Exception as error:
        print(f"Error fetching open role audit tasks: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def add_open_role_audit_task(url: str, extra_notes: Optional[str] = None):
    try:
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
            
        task = await insert_open_role_audit_task(url, extra_notes)
        return task
    except HTTPException:
        raise
    except Exception as error:
        print(f"Error adding open role audit task: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_open_role_audit(task_ids: List[str]):
    try:

        tasks = await get_open_role_audit_tasks_by_ids(task_ids)

        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found with the provided IDs")

        # Update task status to PENDING
        await update_open_role_task_status(task_ids, AuditStatus.PENDING, "Task is pending")

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
        
        return {
            "message": "Open role audit started successfully",
            "tasksCount": len(tasks)
        }
    except HTTPException:
        raise
    except Exception as error:
        print(f"Error starting open role audit: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def delete_open_role_audit_task_controller(task_id: int):
    try:
        # First check if task exists
        tasks = await get_open_role_audit_tasks_by_ids([task_id])
        if not tasks:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Delete the task
        await delete_open_role_audit_task(task_id)
        return {"message": "Open role audit task deleted successfully"}
    except HTTPException:
        raise
    except Exception as error:
        print(f"Error deleting open role audit task: {error}")
        raise HTTPException(status_code=500, detail="Internal server error") 