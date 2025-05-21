from loguru import logger
from src.types.tasks import TaskRequest
from src.services.supabase import update_task_status
from src.types.audit import AuditStatus
from src.agents.closed_role_agent import check_closed_role

async def handle_task(task_request: TaskRequest):
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
        await update_task_status([task_request.taskId], AuditStatus.IN_PROGRESS, "Task is running")
        
        # Log that we would check role here
        response = await check_closed_role(task_request.url)
        
        if not response:
            raise Exception("No result from check_closed_role")
        
        result, screenshot = response
        
        # Log task completion
        await update_task_status([task_request.taskId], AuditStatus.COMPLETED, "Task is complete", {
            "result": result.result,
            "justification": result.justification,
            "screenshot": screenshot
        })
        
        logger.success(f"Task {task_request.taskId} completed successfully")
        return {"message": "Task completed successfully"}

    except Exception as error:
        error_message = str(error)
        logger.error(f"Error processing task {task_request.taskId}: {error_message}")
        await update_task_status([task_request.taskId], AuditStatus.FAILED, error_message)
        raise Exception(error_message) 