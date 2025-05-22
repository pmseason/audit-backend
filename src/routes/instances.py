from fastapi import APIRouter, Query, HTTPException
from src.controllers.instances import list_instances_controller
from typing import List

router = APIRouter(
    prefix="/instances",
    tags=["Instances"]
)

@router.get("/", response_model=List[dict], summary="List Compute Engine instances")
def get_instances(project_id: str = Query(..., description="GCP Project ID"), zone: str = Query(..., description="GCP Zone")):
    try:
        return list_instances_controller(project_id, zone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
