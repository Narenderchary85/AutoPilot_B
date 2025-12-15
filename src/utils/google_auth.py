from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]
CALENDAR_TOKEN = "token_calendar.json"


def get_calendar_credentials():
    creds = None

    if os.path.exists(CALENDAR_TOKEN):
        creds = Credentials.from_authorized_user_file(
            CALENDAR_TOKEN,
            CALENDAR_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                CALENDAR_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(CALENDAR_TOKEN, "w") as token:
            token.write(creds.to_json())

    return creds


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
     "https://www.googleapis.com/auth/gmail.readonly",
]
GMAIL_TOKEN = "token_gmail.json"


def get_gmail_credentials():
    creds = None

    if os.path.exists(GMAIL_TOKEN):
        creds = Credentials.from_authorized_user_file(
            GMAIL_TOKEN,
            GMAIL_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(GMAIL_TOKEN, "w") as token:
            token.write(creds.to_json())

    return creds

CONTACTS_SCOPES = [
    "https://www.googleapis.com/auth/contacts.readonly"
]
CONTACTS_TOKEN = "token_contacts.json"


def get_contacts_credentials():
    creds = None

    if os.path.exists(CONTACTS_TOKEN):
        creds = Credentials.from_authorized_user_file(
            CONTACTS_TOKEN,
            CONTACTS_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",  # Your OAuth client secrets
                CONTACTS_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(CONTACTS_TOKEN, "w") as token:
            token.write(creds.to_json())

    return creds