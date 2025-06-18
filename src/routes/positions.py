from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from src.services.supabase import supabase
from src.types.jobs import JobStatus
from datetime import datetime

router = APIRouter(
    prefix="/positions",
    tags=["Positions"]
)

class UpdatePositionStatusRequest(BaseModel):
    status: Literal["open", "closed"]

@router.put(
    "/{position_id}/status",
    summary="Update position status",
    description="Updates the status of a position to either open or closed",
    responses={
        200: {"description": "Position status updated successfully"},
        400: {"description": "Invalid status value"},
        404: {"description": "Position not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_position_status(position_id: str, request: UpdatePositionStatusRequest):
    try:
        # Validate that the position exists
        position = supabase.from_("positions").select("*").eq("id", position_id).execute()
        if not position.data:
            raise HTTPException(status_code=404, detail="Position not found")

        # Update the position status
        closed_on = datetime.now().strftime("%m/%d/%y") if request.status == "closed" else None
            
        result = supabase.from_("positions").update({
            "status": request.status,
            "closedOn": closed_on
        }).eq("id", position_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update position status")
            
        return {"message": "Position status updated successfully", "data": result.data[0]}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get(
    "/scraped-positions",
    summary="Get positions scraped on a specific date",
    description="Retrieves all positions that were scraped on the given date",
    responses={
        200: {"description": "Successfully retrieved scraped positions"},
        400: {"description": "Invalid date format"},
        500: {"description": "Internal server error"}
    }
)
async def get_scraped_positions(date: str):
    try:
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Query positions scraped on the given date
        result = supabase.from_("scraped_positions") \
            .select("*, company(*, logo(filename_disk))") \
            .gte("createdAt", date) \
            .lt("createdAt", f"{date}T23:59:59") \
            .execute()

        return result.data or []

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
