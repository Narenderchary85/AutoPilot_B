from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class ActivityLog(BaseModel):
    user_id: str
    agent_type: str  # e.g., "email_agent", "calendar_agent"
    user_query: str
    ai_response: str # The text shown to the user
    action_data: Optional[Any] = None # The JSON data from the tool (e.g., event_id)
    status: str = "success" # or "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)