from fastapi import APIRouter, HTTPException
from src.controllers.tasks import handle_closed_role_audit_task, handle_open_role_audit_task
from src.types.tasks import TaskRequest

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/handle")
async def handle_task_route(task_request: TaskRequest):
    """
    Route handler for task processing
    """
    try:
        if task_request.is_closed_role_task:
            return await handle_closed_role_audit_task(task_request)
        elif task_request.is_open_role_task:
            return await handle_open_role_audit_task(task_request)
        else:
            raise HTTPException(status_code=400, detail="Invalid task type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
