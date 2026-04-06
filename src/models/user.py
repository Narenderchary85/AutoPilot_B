from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name:str
    email: EmailStr
    password: str
    isVerified: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str
