from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GoogleTokenBase(BaseModel):
    user_id: str
    scopes: List[str]


class GoogleTokenCreate(GoogleTokenBase):
    access_token: str
    refresh_token: Optional[str] = None
    expiry: datetime
    oauth_state: Optional[str] = None


class GoogleTokenInDB(GoogleTokenCreate):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
