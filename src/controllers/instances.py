from src.services.compute_engine import list_instances as list_instances_service
from typing import List

def list_instances_controller(project_id: str, zone: str) -> List[dict]:
    """
    Controller to get a list of instances in a given project and zone.
    """
    instances = list_instances_service(project_id, zone)
    return instances