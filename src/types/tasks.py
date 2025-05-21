from pydantic import BaseModel

class TaskRequest(BaseModel):
    taskId: int
    type: str
    jobId: str
    url: str 