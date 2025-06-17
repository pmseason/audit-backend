from loguru import logger
from src.types.tasks import TaskRequest
from src.services.supabase import update_closed_role_task_status, update_open_role_task_status, insert_scraped_jobs, get_open_role_audit_tasks_by_ids, get_closed_role_audit_tasks_by_ids
from src.types.audit import AuditStatus
from src.agents.closed_role_agent import ClosedRoleAgent
from src.agents.open_role_agent import find_open_roles
from src.utils.scrape import get_job_postings
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename
from fastapi import HTTPException

async def handle_closed_role_audit_task(task_request: TaskRequest):
    """
    Handles the execution of a task, including status updates and result processing
    
    Args:
        task_request (TaskRequest): Request object containing:
            - type: string - Type of task
            - taskId: string - ID of the task
    """
    try:
        logger.info(f"Starting task processing for taskId: {task_request.taskId}")
        await update_closed_role_task_status([task_request.taskId], AuditStatus.IN_PROGRESS, "Task is running")
        tasks = await get_closed_role_audit_tasks_by_ids([task_request.taskId])
        if not tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        task = tasks[0]
        url = task["job"]["url"]
        clean_url = sanitize_url_for_filename(url)
        setup_logging(clean_url)
        
        # Log that we would check role here
        closed_role_agent = ClosedRoleAgent()
        response = await closed_role_agent.check_job_status(url)
        
        if not response:
            raise Exception("No result from check_closed_role")
        
        result, screenshot = response
        
        # Log task completion
        await update_closed_role_task_status([task_request.taskId], AuditStatus.COMPLETED, "Task is complete", {
            "result": result.result,
            "justification": result.justification,
            "screenshot": screenshot
        })
        
        logger.success(f"Task {task_request.taskId} completed successfully")
        await upload_logs_to_cloud(clean_url, f"closed_role_audit")
        return {"message": "Task completed successfully"}

    except Exception as error:
        error_message = str(error)
        logger.error(f"Error processing task {task_request.taskId}: {error_message}")
        await update_closed_role_task_status([task_request.taskId], AuditStatus.FAILED, error_message)
        await upload_logs_to_cloud(clean_url, f"closed_role_audit")
        raise
    
async def handle_open_role_audit_task(task_request: TaskRequest):
    """
    Handles the execution of an open role audit task, including status updates and result processing
    
    Args:
        task_request (TaskRequest): Request object containing:
            - type: string - Type of task 
            - url: string - URL to be processed
            - taskId: string - ID of the task
            - extra_notes: string - Optional additional notes
    """
    try:
        logger.info(f"Starting open role audit task processing for taskId: {task_request.taskId}")
        await update_open_role_task_status([task_request.taskId], AuditStatus.IN_PROGRESS, "Task is running")
        task = await get_open_role_audit_tasks_by_ids([task_request.taskId])
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task = task[0]
        
        url = task["url"]
        clean_url = sanitize_url_for_filename(url)
        setup_logging(clean_url)
        
        jobs_found = await get_job_postings(url, task["id"], task["company"])
        logger.info(f"Number of jobs found: {len(jobs_found)}")
        logger.info(f"Jobs found: {jobs_found}")
    
        
        # Log task completion
        await update_open_role_task_status([task_request.taskId], AuditStatus.COMPLETED, "Task is complete")
        
        logger.success(f"Open role audit task {task_request.taskId} completed successfully")
        await upload_logs_to_cloud(clean_url, f"open_role_audit")
        return {"message": "Task completed successfully"}

    except Exception as error:
        error_message = str(error)
        logger.error(f"Error processing open role audit task {task_request.taskId}: {error_message}")
        await update_open_role_task_status([task_request.taskId], AuditStatus.FAILED, error_message)
        await upload_logs_to_cloud(clean_url, f"open_role_audit")
        raise