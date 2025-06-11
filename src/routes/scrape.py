from fastapi import APIRouter, Body
from typing import List, Optional
from pydantic import BaseModel
from src.controllers.scrape import start_scrape_roles, post_scrape_results_controller

router = APIRouter(
    prefix="/scrape",
    tags=["Scrape"]
)

class ScrapeRequest(BaseModel):
    url: str
    extra_notes: Optional[str] = None

class StartScrapeRequest(BaseModel):
    taskIds: List[int]

@router.post("/start",
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
    return await start_scrape_roles()

@router.post("/results",
    summary="Get scrape results",
    description="Returns the current status of scrape tasks",
    responses={
        200: {"description": "Successfully retrieved scrape status"},
        500: {"description": "Internal server error"}
    }
)
async def post_scrape_results():
    return await post_scrape_results_controller()