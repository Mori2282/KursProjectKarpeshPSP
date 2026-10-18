from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database.models import TaskStatus

class TaskResponse(BaseModel):
    id: str
    status: TaskStatus
    original_filename: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BatchUploadResponse(BaseModel):
    enqueued_tasks: List[TaskResponse]
