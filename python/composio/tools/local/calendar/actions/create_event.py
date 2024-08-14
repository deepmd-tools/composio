from pydantic import BaseModel, Field
from datetime import datetime
from urllib.parse import urlencode
from composio.tools.local.base import Action


class CreateEventRequest(BaseModel):
    title: str = Field(..., description="Event title")
    start_time: datetime = Field(..., description="Start time of the event")
    end_time: datetime = Field(..., description="End time of the event")
    description: str = Field("", description="Description of the event")
    location: str = Field("", description="Location of the event")
    guests: str = Field("", description="Comma-separated list of guest emails")
    recurrence: str = Field("", description="Recurrence rule (RFC-5545 format)")


class CreateEventResponse(BaseModel):
    event_link: str = Field(..., description="Google Calendar event creation link")


class CreateEvent(Action[CreateEventRequest, CreateEventResponse]):
    """
    Useful to create a Google Calendar event link.
    """

    _display_name = "Create Google Calendar Event"
    _request_schema = CreateEventRequest
    _response_schema = CreateEventResponse
    _tags = ["calendar"]
    _tool_name = "calendar"

    def execute(
        self, request_data: CreateEventRequest, authorisation_data: dict
    ) -> dict:
        base_url = "https://calendar.google.com/calendar/render"
        
        params = {
            "action": "TEMPLATE",
            "text": request_data.title,
            "dates": f"{request_data.start_time.strftime('%Y%m%dT%H%M%SZ')}/{request_data.end_time.strftime('%Y%m%dT%H%M%SZ')}",
            "details": request_data.description,
            "location": request_data.location,
        }

        if request_data.guests:
            params["add"] = request_data.guests

        if request_data.recurrence:
            params["recur"] = f"RRULE:{request_data.recurrence}"

        event_link = f"{base_url}?{urlencode(params)}"

        execution_details = {"executed": True}
        response_data = {"event_link": event_link}

        return {"execution_details": execution_details, "response_data": response_data}
