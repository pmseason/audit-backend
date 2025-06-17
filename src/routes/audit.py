from fastapi import APIRouter, Body
from typing import List, Optional
from pydantic import BaseModel
from src.controllers.audit import (
    start_closed_role_audit,
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

class StartClosedRoleAuditRequest(BaseModel):
    taskIds: List[int]

class AddOpenRoleAuditRequest(BaseModel):
    url: str

class StartOpenRoleAuditRequest(BaseModel):
    taskIds: List[int]

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