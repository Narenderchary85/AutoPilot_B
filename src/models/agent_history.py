from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    completed = "completed"
    failed = "failed"
    in_progress = "in-progress"


class AgentHistory(BaseModel):
    task_name: str
    task_description: str
    agent_type: str
    status: AgentStatus
    execution_time: float

    user_id: str
    result_summary: Optional[str]

    created_at: datetime = Field(default_factory=datetime.utcnow)
