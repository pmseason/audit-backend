from pydantic import BaseModel

class TaskRequest(BaseModel):
    taskId: int
    type: str
    url: str
    jobId: str | None = None
    extra_notes: str | None = None
    site: str | None = None
    
    @property
    def is_closed_role_task(self) -> bool:
        return self.type == "CLOSED_ROLE_AUDIT"

    @property 
    def is_open_role_task(self) -> bool:
        return self.type == "OPEN_ROLE_AUDIT"