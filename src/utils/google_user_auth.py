from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from src.db.mongo import google_tokens_collection
import os

def get_user_credentials(user_id: str):
    """Fetch and refresh Google credentials for a specific user from the DB."""
    token_doc = google_tokens_collection.find_one({"user_id": user_id})
    
    if not token_doc:
        raise Exception(f"Google account not connected for user: {user_id}")

    creds = Credentials(
        token=token_doc["access_token"],
        refresh_token=token_doc.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=token_doc["scopes"]
    )

    # Automatically refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Update the DB with the new access token
        google_tokens_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "access_token": creds.token,
                "expiry": creds.expiry
            }}
        )

    return creds