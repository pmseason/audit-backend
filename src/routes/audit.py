from fastapi import APIRouter, HTTPException
from loguru import logger
from src.controllers.audit import (
    get_all_closed_role_audit_tasks,
    start_closed_role_audit,
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

@router.post("/start/closed",
    summary="Start closed role audit",
    description="Creates cloud tasks for specified closed role audit tasks",
    responses={
        200: {"description": "Closed role audit started successfully"},
        400: {"description": "Invalid request - taskIds must be an array of integers"},
        404: {"description": "No tasks found with the provided IDs"},
        500: {"description": "Internal server error"}
    }
)
async def start_closed_role_audit_route():
    return await start_closed_role_audit()

@router.get("/closed",
    summary="Get all closed role audit tasks",
    description="Retrieves all closed role audit tasks with their associated job and company information",
    responses={
        200: {"description": "Successfully retrieved all closed role audit tasks"},
        500: {"description": "Internal server error"}
    }
)
async def get_all_closed_role_audit_tasks_route():    
    try:
        tasks = await get_all_closed_role_audit_tasks()
        return tasks
    except Exception as error:
        logger.error(f"Error getting all closed role audit tasks: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")
