from fastapi import APIRouter, HTTPException
from src.controllers.tasks import handle_task
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
        return await handle_task(task_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
