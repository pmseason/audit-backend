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
