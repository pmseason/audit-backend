from fastapi import APIRouter, Body, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from src.controllers.scrape import start_scrape_role

router = APIRouter(
    prefix="/scrape",
    tags=["Scraper"]
)

@router.post("/start",
    summary="Start scraping roles",
    description="Starts scraping roles in the background",
    responses={
        200: {"description": "Scraping started successfully"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)
async def start_scrape_role_route(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_scrape_role)
    return {"message": "Scraping started successfully in the background"}