from datetime import datetime, timedelta
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.google_auth import get_calendar_credentials


class AddEventToCalendarInput(BaseModel):
    title: str = Field(description="Title of the event")
    description: str = Field(description="Description of the event")
    start_time: str = Field(
        description="Start time of the event in ISO format (YYYY-MM-DDTHH:MM:SS±TZ)"
    )


@tool(
    "AddEventToCalendar",
    args_schema=AddEventToCalendarInput
)
@traceable(run_type="tool", name="AddEventToCalendar")
def add_event_to_calendar(
    title: str,
    description: str,
    start_time: str
):
    """
    Creates a Google Calendar event.
    This is a LangChain StructuredTool and MUST be called via `.invoke()`
    """

    try:
        creds = get_calendar_credentials()

        service = build("calendar", "v3", credentials=creds)

        event_start = datetime.fromisoformat(start_time)

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": event_start.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": (event_start + timedelta(hours=1)).isoformat(),
                "timeZone": "UTC",
            },
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return {
            "message": "Event created successfully",
            "event_id": created_event.get("id"),
            "html_link": created_event.get("htmlLink"),
        }

    except HttpError as error:
        return {
            "error": "Google Calendar API error",
            "details": str(error),
        }
