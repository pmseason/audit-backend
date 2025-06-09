from loguru import logger
from src.types.tasks import TaskRequest
from src.services.supabase import update_closed_role_task_status, update_open_role_task_status, insert_scraped_jobs, delete_scraped_jobs_by_task_id
from src.types.audit import AuditStatus
from src.agents.closed_role_agent import check_closed_role
from src.agents.open_role_agent import find_open_roles
from src.utils.scrape import get_job_postings
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename

async def handle_closed_role_audit_task(task_request: TaskRequest):
    """
    Handles the execution of a task, including status updates and result processing
    
    Args:
        task_request (TaskRequest): Request object containing:
            - type: string - Type of task
            - jobId: string - ID of the job
            - url: string - URL to be processed
            - taskId: string - ID of the task
    """
    try:
        logger.info(f"Starting task processing for taskId: {task_request.taskId}")
        await update_closed_role_task_status([task_request.taskId], AuditStatus.IN_PROGRESS, "Task is running")
        
        # Log that we would check role here
        response = await check_closed_role(task_request.url)
        
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
        return {"message": "Task completed successfully"}

    except Exception as error:
        error_message = str(error)
        logger.error(f"Error processing task {task_request.taskId}: {error_message}")
        await update_closed_role_task_status([task_request.taskId], AuditStatus.FAILED, error_message)
        raise Exception(error_message)
    
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
        
        url = task_request.url
        clean_url = sanitize_url_for_filename(url)
        setup_logging(clean_url)
        jobs_found = await get_job_postings(url, task_request.taskId)
        logger.info(f"Number of jobs found: {len(jobs_found)}")
        logger.info(f"Jobs found: {jobs_found}")
        
        
        if not jobs_found:
            raise Exception("No result from get_job_postings")
            
            # jobs are inserted in the get_job_postings function
        # await insert_scraped_jobs(jobs_found, task_request.taskId)
        
        # Log task completion
        await update_open_role_task_status([task_request.taskId], AuditStatus.COMPLETED, "Task is complete")
        
        logger.success(f"Open role audit task {task_request.taskId} completed successfully")
        return {"message": "Task completed successfully"}

    except Exception as error:
        error_message = str(error)
        logger.error(f"Error processing open role audit task {task_request.taskId}: {error_message}")
        await update_open_role_task_status([task_request.taskId], AuditStatus.FAILED, error_message)
    finally:
        await upload_logs_to_cloud(clean_url)