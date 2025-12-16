from fastapi import APIRouter, Depends, Request, HTTPException
from google_auth_oauthlib.flow import Flow
from src.utils.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from src.db.mongo import google_tokens_collection
from src.auth.dependencies import get_current_user
from src.models.google_token import GoogleTokenCreate
from datetime import datetime
import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

router = APIRouter(prefix="/google", tags=["Google"])

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/calendar"
]

@router.get("/connect")
def connect_google(user_id: str = Depends(get_current_user)):
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/google/callback"
    )

    auth_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline"
    )

    google_tokens_collection.update_one(
        {"user_id": user_id},
        {"$set": {"oauth_state": state}},
        upsert=True
    )

    return {"auth_url": auth_url}

@router.get("/callback")
def google_callback(request: Request):
    state = request.query_params.get("state")

    user_record = google_tokens_collection.find_one({"oauth_state": state})
    if not user_record:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    user_id = user_record["user_id"]

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/google/callback",
        state=state
    )

    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    token_data = GoogleTokenCreate(
        user_id=user_id,
        access_token=creds.token,
        refresh_token=creds.refresh_token,
        scopes=creds.scopes,
        expiry=creds.expiry,
        oauth_state=None
    )

    google_tokens_collection.update_one(
        {"user_id": user_id},
        {"$set": token_data.dict()},
        upsert=True
    )

    return {"message": "Google account connected"}
