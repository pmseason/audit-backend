from fastapi import APIRouter, Body
from typing import List, Optional
from pydantic import BaseModel
from src.controllers.audit import (
    create_closed_role_audit,
    start_closed_role_audit,
    get_closed_role_audit_tasks,
    get_open_role_audit_tasks,
    add_open_role_audit_task,
    start_open_role_audit,
    delete_open_role_audit_task_controller
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

class StartClosedRoleAuditRequest(BaseModel):
    taskIds: List[int]

class AddOpenRoleAuditRequest(BaseModel):
    url: str
    extra_notes: Optional[str] = None

class StartOpenRoleAuditRequest(BaseModel):
    taskIds: List[int]

@router.post("/create/closed", 
    summary="Create a closed role audit",
    description="Creates a new closed role audit",
    responses={
        200: {"description": "Closed role audit created successfully"},
        500: {"description": "Internal server error"}
    }
)
async def create_closed_role_audit_route():
    return await create_closed_role_audit()

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
async def start_closed_role_audit_route(request: StartClosedRoleAuditRequest):
    return await start_closed_role_audit(request.taskIds)

@router.get("/closed",
    summary="Get all closed role audit tasks",
    description="Retrieves all closed role audit tasks",
    responses={
        200: {"description": "List of closed role audit tasks"},
        500: {"description": "Internal server error"}
    }
)
async def get_closed_role_audit_tasks_route():
    return await get_closed_role_audit_tasks()

@router.get("/open",
    summary="Get all open role audit tasks",
    description="Retrieves all open role audit tasks",
    responses={
        200: {"description": "List of open role audit tasks"},
        500: {"description": "Internal server error"}
    }
)
async def get_open_role_audit_tasks_route():
    return await get_open_role_audit_tasks()

@router.post("/add/open",
    summary="Add a new open role audit task",
    description="Creates a new open role audit task with the provided URL and optional notes",
    responses={
        200: {"description": "Open role audit task created successfully"},
        400: {"description": "Invalid request - URL is required"},
        500: {"description": "Internal server error"}
    }
)
async def add_open_role_audit_task_route(request: AddOpenRoleAuditRequest):
    return await add_open_role_audit_task(request.url, request.extra_notes)

@router.post("/start/open",
    summary="Start open role audit",
    description="Creates cloud tasks for specified open role audit tasks",
    responses={
        200: {"description": "Open role audit started successfully"},
        400: {"description": "Invalid request - taskIds must be an array of integers"},
        404: {"description": "No tasks found with the provided IDs"},
        500: {"description": "Internal server error"}
    }
)
async def start_open_role_audit_route(request: StartOpenRoleAuditRequest):
    return await start_open_role_audit(request.taskIds)

@router.delete("/open/{task_id}",
    summary="Delete an open role audit task",
    description="Deletes a specific open role audit task by its ID",
    responses={
        200: {"description": "Open role audit task deleted successfully"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_open_role_audit_task_route(task_id: int):
    return await delete_open_role_audit_task_controller(task_id)