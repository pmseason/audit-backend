from fastapi import APIRouter, Query, HTTPException
from src.controllers.instances import list_instances_controller
from typing import List

router = APIRouter(
    prefix="/instances",
    tags=["Instances"]
)

@router.get("/", summary="List Compute Engine instances")
def get_instances():
    try:
        return list_instances_controller()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
