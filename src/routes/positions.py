from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from src.services.supabase import supabase
from src.types.jobs import JobStatus
from datetime import datetime
from src.services.directus import add_position_to_directus, update_position_in_directus

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
        # result = supabase.from_("positions").update({
        #     "status": request.status
        # }).eq("id", position_id).execute()
        
        # we need to directly post to directus
        result = await update_position_in_directus(position_id, {
            "status": request.status
        })
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update position status")
            
        return {"message": "Position status updated successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/{scraped_position_id}/promote",
    summary="Promote scraped position to positions table",
    description="Takes a scraped_position id and adds the data to the positions table",
    responses={
        200: {"description": "Position promoted successfully"},
        404: {"description": "Scraped position not found"},
        409: {"description": "Position already exists in positions table"},
        500: {"description": "Internal server error"}
    }
)
async def promote_scraped_position(scraped_position_id: str):
    try:
        # Get the scraped position data
        scraped_position = supabase.from_("scraped_positions").select("*, company(*)").eq("id", scraped_position_id).execute()
        if not scraped_position.data:
            raise HTTPException(status_code=404, detail="Scraped position not found")
        
        scraped_data = scraped_position.data[0]
        
        # Check if position already exists in positions table (by URL)
        existing_position = supabase.from_("positions").select("*").eq("url", scraped_data["url"]).execute()
        if existing_position.data:
            raise HTTPException(status_code=409, detail="Position already exists in positions table")
        
        # Map scraped_position fields to positions table fields
        position_data = {
            "title": scraped_data["title"],
            "url": scraped_data["url"],
            "description": scraped_data["description"],
            "jobType": scraped_data["jobType"],
            "status": "open",  # Default to open when promoting
            "company": scraped_data["company"]["id"],
            "salaryText": scraped_data["salaryText"],
            "visaSponsored": scraped_data["visaSponsored"],
            "location": scraped_data["location"],
            "other": scraped_data["other"],
            "site": scraped_data["site"],
            "hidden": False,  # Default to visible
            "scraped_position": scraped_position_id,
            "min_years_experience": scraped_data["min_years_experience"],
            "min_education_level": scraped_data["min_education_level"]
        }
        
        # we need to directly post to directus
        result = await add_position_to_directus(position_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to promote position")
            
        return {
            "message": "Position promoted successfully"
        }
        
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
            .select("*, company(*, logo(filename_disk)), positions(id)") \
            .gte("createdAt", date) \
            .lt("createdAt", f"{date}T23:59:59") \
            .order("createdAt") \
            .execute()

        return result.data or []

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/{scraped_position_id}",
    summary="Delete positions by scraped position ID",
    description="Deletes all positions where the scraped_position field matches the provided scraped_position_id",
    responses={
        200: {"description": "Positions deleted successfully"},
        404: {"description": "No positions found with the given scraped_position_id"},
        500: {"description": "Internal server error"}
    }
)
async def delete_positions_by_scraped_position_id(scraped_position_id: str):
    try:
        # First, check if any positions exist with this scraped_position_id
        existing_positions = supabase.from_("positions").select("id").eq("scraped_position", scraped_position_id).execute()
        
        if not existing_positions.data:
            raise HTTPException(status_code=404, detail="No positions found with the given scraped_position_id")
        
        # Delete all positions with the matching scraped_position_id
        result = supabase.from_("positions").delete().eq("scraped_position", scraped_position_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to delete positions")
            
        return {
            "message": f"Successfully deleted {len(result.data)} position(s)",
            "deleted_count": len(result.data),
            "data": result.data
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
