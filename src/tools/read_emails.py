# from datetime import datetime, timezone
# from typing import Optional, List, Dict
# from langsmith import traceable
# from langchain_core.tools import tool
# from pydantic import BaseModel, Field
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from email.utils import parsedate_to_datetime
# from src.utils.google_user_auth import get_user_credentials


# class ReadEmailsInput(BaseModel):
#     from_date: str = Field(description="From date for reading emails (ISO format)")
#     to_date: str = Field(description="To date for reading emails (ISO format)")
#     email: Optional[str] = Field(default=None, description="Optional sender email filter")
#     user_id: str = Field(description="Authenticated user ID")


# @tool("ReadEmails", args_schema=ReadEmailsInput)
# @traceable(run_type="tool", name="ReadEmails")
# def read_emails(
#     from_date: str,
#     to_date: str,
#     email: Optional[str],
#     user_id: str
# ):
#     """
#     Read unread emails from Gmail within a date range,
#     optionally filtered by sender email.
#     """
#     try:
#         # Get OAuth credentials for the user
#         creds = get_user_credentials(user_id)
#         service = build("gmail", "v1", credentials=creds)

#         from_ts = int(datetime.fromisoformat(from_date).timestamp())
#         to_ts = int(datetime.fromisoformat(to_date).timestamp())

#         query = f"is:unread after:{from_ts} before:{to_ts}"
#         if email:
#             query += f" from:{email}"

#         results = service.users().messages().list(
#             userId="me",
#             q=query,
#             maxResults=20
#         ).execute()
#         print("results:",results)

#         messages = results.get("messages", [])
#         if not messages:
#             return []
#         print("messages:",messages)

#         email_list: List[Dict] = []

#         for message in messages:
#             msg = service.users().messages().get(
#                 userId="me",
#                 id=message["id"],
#                 format="metadata",
#                 metadataHeaders=["From", "Subject", "Date"]
#             ).execute()
#             print("msg:",msg)

#             headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

#             date_str = headers.get("Date", "")
#             try:
#                 date_obj = parsedate_to_datetime(date_str)
#                 if date_obj and date_obj.tzinfo is None:
#                     date_obj = date_obj.replace(tzinfo=timezone.utc)
#                 date_iso = date_obj.isoformat() if date_obj else date_str
#             except Exception:
#                 date_iso = date_str

#             email_list.append({
#                 "id": msg["id"],
#                 "from": headers.get("From", "Unknown Sender"),
#                 "subject": headers.get("Subject", "No Subject"),
#                 "date": date_iso,
#                 "snippet": msg.get("snippet", "")
#             })
#             print("email_list:",email_list)
#         return email_list

#     except HttpError as error:
#         return {"error": str(error)}

from datetime import datetime, timezone
from typing import Optional, List, Dict
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.utils import parsedate_to_datetime
from src.utils.google_user_auth import get_user_credentials


# -------------------------------
# INPUT SCHEMA
# -------------------------------
class ReadEmailsInput(BaseModel):
    from_date: str = Field(description="From date for reading emails (ISO format)")
    to_date: str = Field(description="To date for reading emails (ISO format)")
    email: Optional[str] = Field(default=None, description="Optional sender email filter")
    user_id: str = Field(description="Authenticated user ID")


# -------------------------------
# TOOL
# -------------------------------
@tool("ReadEmails", args_schema=ReadEmailsInput)
@traceable(run_type="tool", name="ReadEmails")
def read_emails(
    from_date: str,
    to_date: str,
    email: Optional[str],
    user_id: str
):
    """
    Read unread emails from Gmail within a date range
    """

    print("\n========== ReadEmails TOOL START ==========")
    print("from_date:", from_date)
    print("to_date:", to_date)
    print("email filter:", email)
    print("user_id:", user_id)

    try:
        # -------------------------------
        # STEP 1: AUTH
        # -------------------------------
        print("\n[STEP 1] Fetching user credentials...")

        creds = get_user_credentials(user_id)

        if not creds:
            print("❌ ERROR: No credentials returned")
            return {"error": "User credentials not found"}

        print("✅ Credentials fetched")

        # -------------------------------
        # STEP 2: BUILD GMAIL SERVICE
        # -------------------------------
        print("\n[STEP 2] Building Gmail service...")

        service = build("gmail", "v1", credentials=creds)

        print("✅ Gmail service created")

        # -------------------------------
        # STEP 3: DATE PARSING
        # -------------------------------
        print("\n[STEP 3] Parsing date range...")

        from_ts = int(datetime.fromisoformat(from_date).timestamp())
        to_ts = int(datetime.fromisoformat(to_date).timestamp())

        print("from_ts:", from_ts)
        print("to_ts:", to_ts)

        # -------------------------------
        # STEP 4: BUILD QUERY
        # -------------------------------
        print("\n[STEP 4] Building Gmail query...")

        query = f"is:unread after:{from_ts} before:{to_ts}"
        if email:
            query += f" from:{email}"

        print("Gmail query:", query)

        # -------------------------------
        # STEP 5: LIST MESSAGES
        # -------------------------------
        print("\n[STEP 5] Fetching message list...")

        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=20
        ).execute()

        print("Raw list response:", results)

        messages = results.get("messages", [])

        if not messages:
            print("⚠️ No unread emails found")
            return []

        print(f"✅ Found {len(messages)} messages")

        # -------------------------------
        # STEP 6: FETCH MESSAGE DETAILS
        # -------------------------------
        print("\n[STEP 6] Fetching individual email metadata...")

        email_list: List[Dict] = []

        for idx, message in enumerate(messages, start=1):
            print(f"\n--- Processing message {idx} ---")
            print("Message ID:", message.get("id"))

            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            print("Raw message data:", msg)

            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

            date_str = headers.get("Date", "")
            try:
                date_obj = parsedate_to_datetime(date_str)
                if date_obj and date_obj.tzinfo is None:
                    date_obj = date_obj.replace(tzinfo=timezone.utc)
                date_iso = date_obj.isoformat() if date_obj else date_str
            except Exception as e:
                print("⚠️ Date parsing failed:", e)
                date_iso = date_str

            email_data = {
                "id": msg.get("id"),
                "from": headers.get("From", "Unknown Sender"),
                "subject": headers.get("Subject", "No Subject"),
                "date": date_iso,
                "snippet": msg.get("snippet", "")
            }

            print("Parsed email:", email_data)

            email_list.append(email_data)

        # -------------------------------
        # STEP 7: RETURN
        # -------------------------------
        print("\n[STEP 7] Returning email list")
        print("Total emails returned:", len(email_list))

        print("========== ReadEmails TOOL END ==========\n")

        return email_list

    except HttpError as error:
        print("❌ GMAIL API ERROR:", error)
        return {"error": str(error)}

    except Exception as e:
        print("❌ UNEXPECTED ERROR:", e)
        return {"error": str(e)}
