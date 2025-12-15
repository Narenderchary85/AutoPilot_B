from datetime import datetime, timezone
from typing import Optional, List, Dict
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.utils import parsedate_to_datetime
from src.utils.google_auth import get_gmail_credentials


class ReadEmailsInput(BaseModel):
    from_date: str = Field(description="From date for reading emails (ISO format)")
    to_date: str = Field(description="To date for reading emails (ISO format)")
    email: Optional[str] = Field(description="Optional sender email filter")


@tool("ReadEmails", args_schema=ReadEmailsInput)
@traceable(run_type="tool", name="ReadEmails")
def read_emails(from_date: str, to_date: str, email: Optional[str] = None):
    """
    Reads emails from Gmail inbox and returns structured email data.
    """

    try:
        creds = get_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

        from_ts = int(datetime.fromisoformat(from_date).timestamp())
        to_ts = int(datetime.fromisoformat(to_date).timestamp())

        query = f"is:unread after:{from_ts} before:{to_ts}"
        if email:
            query += f" from:{email}"

        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=20
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return []

        email_list: List[Dict] = []

        for message in messages:
            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

            date_str = headers.get("Date", "")
            try:
                date_obj = parsedate_to_datetime(date_str)
                if date_obj and date_obj.tzinfo is None:
                    date_obj = date_obj.replace(tzinfo=timezone.utc)
                date_iso = date_obj.isoformat() if date_obj else date_str
            except Exception:
                date_iso = date_str

            email_list.append({
                "id": msg["id"],
                "from": headers.get("From", "Unknown Sender"),
                "subject": headers.get("Subject", "No Subject"),
                "date": date_iso,
                "snippet": msg.get("snippet", "")
            })

        return email_list

    except HttpError as error:
        return {
            "error": str(error)
        }
