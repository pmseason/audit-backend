from pydantic import BaseModel

class TaskRequest(BaseModel):
    taskId: int
    type: str
    
    @property
    def is_closed_role_task(self) -> bool:
        return self.type == "CLOSED_ROLE_AUDIT"

    @property 
    def is_open_role_task(self) -> bool:
        return self.type == "OPEN_ROLE_AUDIT"