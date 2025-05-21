from fastapi import APIRouter, Body
from typing import List
from pydantic import BaseModel
from src.controllers.audit import (
    create_closed_role_audit,
    start_closed_role_audit,
    get_closed_role_audit_tasks
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

class StartClosedRoleAuditRequest(BaseModel):
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