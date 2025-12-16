from jose import jwt
from datetime import datetime, timedelta
from src.utils.config import JWT_SECRET, JWT_ALGORITHM

def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=12)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
