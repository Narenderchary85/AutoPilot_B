import base64
from email.mime.text import MIMEText
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from src.utils.google_auth import get_gmail_credentials
from src.utils.google_user_auth import get_user_credentials


class SendEmailInput(BaseModel):
    to: str | list = Field(description="Recipient email(s)")
    subject: str
    body: str
    user_id: str = Field(description="User ID for OAuth credentials")


@tool("SendEmail", args_schema=SendEmailInput)
def send_email(to, subject: str, body: str, user_id: str):
    """
    Send email using Gmail API (OAuth)
    """

    if isinstance(to, list):
        recipients = to
    else:
        recipients = [to]
    print("user id in send email tool:",user_id)
    #creds = get_gmail_credentials()
    creds = get_user_credentials(user_id)
    service = build("gmail", "v1", credentials=creds)

    results = []

    for recipient in recipients:
        message = MIMEText(body)
        message["to"] = recipient
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

        sent = service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()

        results.append({
            "to": recipient,
            "message_id": sent["id"]
        })

    return {
        "status": "success",
        "sent": results
    }
