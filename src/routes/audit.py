from fastapi import APIRouter, HTTPException
from loguru import logger
from src.controllers.audit import (
    get_all_closed_role_audit_tasks,
    start_closed_role_audit,
    start_open_role_audit,
    post_open_role_audit_results,
)
from src.services.supabase import get_all_open_role_audit_tasks

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
    

@router.post("/start/open",
    summary="Start scrape tasks",
    description="Creates cloud tasks for specified scrape tasks",
    responses={
        200: {"description": "Scrape tasks started successfully"},
        400: {"description": "Invalid request - taskIds must be an array of integers"},
        404: {"description": "No tasks found with the provided IDs"},
        500: {"description": "Internal server error"}
    }
)
async def scrape_open_jobs():
    return await start_open_role_audit()

@router.post("/results",
    summary="Get scrape results",
    description="Returns the current status of scrape tasks",
    responses={
        200: {"description": "Successfully retrieved scrape status"},
        500: {"description": "Internal server error"}
    }
)
async def post_scrape_results():
    return await post_open_role_audit_results()


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
    

@router.get("/open",
    summary="Get all open role audit tasks",
    description="Retrieves all open role audit tasks with their associated company information",
    responses={
        200: {"description": "Successfully retrieved all open role audit tasks"},
        500: {"description": "Internal server error"}
    }
)
async def get_all_open_role_audit_tasks_route():    
    try:
        tasks = await get_all_open_role_audit_tasks()
        return tasks
    except Exception as error:
        logger.error(f"Error getting all open role audit tasks: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

