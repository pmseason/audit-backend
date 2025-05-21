from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    message: str

async def health_check() -> HealthResponse:
    """
    Health check implementation to verify if the API is running.
    
    Returns:
        HealthResponse: A response containing the status and message
    """
    return HealthResponse(
        status="healthy",
        message="API is running"
    ) 