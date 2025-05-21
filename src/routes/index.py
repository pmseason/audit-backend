from fastapi import APIRouter, status
from src.controllers.index import health_check, HealthResponse

router = APIRouter(
    prefix="",
    tags=["Health"]
)

@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running"
)
async def get_health():
    """
    Health check endpoint to verify if the API is running.
    
    Returns:
        HealthResponse: A response containing the status and message
    """
    return await health_check() 