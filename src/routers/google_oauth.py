from fastapi import APIRouter, Depends, Request
from google_auth_oauthlib.flow import Flow
from src.utils.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from src.db.mongo import google_tokens_collection
import os

router = APIRouter(prefix="/google", tags=["Google"])

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/calendar"
]

@router.get("/connect")
def connect_google():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/google/callback"
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return {"auth_url": auth_url}

@router.get("/callback")
def google_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/google/callback"
    )

    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    google_tokens_collection.insert_one({
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "scope": creds.scopes,
        "expiry": creds.expiry
    })

    return {"message": "Google account connected"}
