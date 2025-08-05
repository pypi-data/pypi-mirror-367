import os
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Optional, Annotated
from pydantic import Field
from datetime import datetime

mcp = FastMCP("netmind-mcpserver-mcp")

creds = Credentials(
    token=os.environ["GOOGLE_ACCESS_TOKEN"],
    refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    scopes=[
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ]
)
service = build("calendar", "v3", credentials=creds)


@mcp.tool(description="List all available calendars")
async def list_calendars():
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get("items", [])


@mcp.tool(description="List events from one or more calendars.")
async def list_events(
        calendar_id: Annotated[
            str, Field(
                description=(
                        "ID of the calendar(s) to list events from. Accepts either a single calendar ID string "
                        "or an array of calendar IDs (passed as JSON string like '[\"cal1\", \"cal2\"]')"
                )
            )
        ] = "primary",
        time_min: Annotated[
            Optional[str], Field(
                description=(
                        "Start time boundary. Preferred: '2024-01-01T00:00:00' (uses timeZone parameter or calendar timezone). "
                        "Also accepts: '2024-01-01T00:00:00Z' or '2024-01-01T00:00:00-08:00'."
                )
            )
        ] = None,
        time_max: Annotated[
            Optional[str], Field(
                description=(
                        "End time boundary. Preferred: '2024-01-01T23:59:59' (uses timeZone parameter or calendar timezone). "
                        "Also accepts: '2024-01-01T23:59:59Z' or '2024-01-01T23:59:59-08:00'."
                )
            )
        ] = None,
        time_zone: Annotated[
            Optional[str], Field(
                description=(
                        "Timezone as IANA Time Zone Database name (e.g., America/Los_Angeles). "
                        "Takes priority over calendar's default timezone. Only used for timezone-naive datetime strings."
                )
            )
        ] = None
):
    now = datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min or now,
        timeMax=time_max,
        timeZone=time_zone,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events.get("items", [])


@mcp.tool(description="Search for events in a calendar by text query.")
async def search_events(
        calendar_id: Annotated[
            str, Field(description="ID of the calendar (use 'primary' for the main calendar)")
        ] = "primary",
        query: Annotated[
            str, Field(description="Free text search query (searches summary, description, location, attendees, etc.)")
        ] = "",
        time_min: Annotated[
            Optional[str], Field(
                description=(
                        "Start time boundary. Preferred: '2024-01-01T00:00:00' (uses timeZone parameter or calendar timezone). "
                        "Also accepts: '2024-01-01T00:00:00Z' or '2024-01-01T00:00:00-08:00'."
                )
            )
        ] = None,
        time_max: Annotated[
            Optional[str], Field(
                description=(
                        "End time boundary. Preferred: '2024-01-01T23:59:59' (uses timeZone parameter or calendar timezone). "
                        "Also accepts: '2024-01-01T23:59:59Z' or '2024-01-01T23:59:59-08:00'."
                )
            )
        ] = None,
        time_zone: Annotated[
            Optional[str], Field(
                description=(
                        "Timezone as IANA Time Zone Database name (e.g., America/Los_Angeles). "
                        "Takes priority over calendar's default timezone. Only used for timezone-naive datetime strings."
                )
            )
        ] = None
):
    events = service.events().list(
        calendarId=calendar_id,
        q=query,
        timeMin=time_min,
        timeMax=time_max,
        timeZone=time_zone,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events.get("items", [])


@mcp.tool(description="Create a new calendar event.")
async def create_event(
        calendar_id: Annotated[
            str, Field(description="ID of the calendar (use 'primary' for the main calendar)")
        ] = "primary",
        summary: Annotated[
            str, Field(description="Title of the event")
        ] = "",
        description: Annotated[
            Optional[str], Field(description="Description/notes for the event")
        ] = None,
        start: Annotated[
            str, Field(description="Event start time: '2024-01-01T10:00:00'")
        ] = "",
        end: Annotated[
            str, Field(description="Event end time: '2024-01-01T11:00:00'")
        ] = "",
        time_zone: Annotated[
            Optional[str], Field(
                description="Timezone as IANA Time Zone Database name (e.g., America/Los_Angeles). Takes priority over calendar's default timezone. Only used for timezone-naive datetime strings.")
        ] = None,
        location: Annotated[
            Optional[str], Field(description="Location of the event")
        ] = None,
        attendees: Annotated[
            Optional[List[dict]], Field(description="List of attendee email addresses")
        ] = None,
        color_id: Annotated[
            Optional[str], Field(description="Color ID for the event (use list-colors to see available IDs)")
        ] = None,
        reminders: Annotated[
            Optional[dict], Field(description="Reminder settings for the event")
        ] = None,
        recurrence: Annotated[
            Optional[List[str]], Field(
                description="Recurrence rules in RFC5545 format (e.g., ['RRULE:FREQ=WEEKLY;COUNT=5'])")
        ] = None
):
    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start, "timeZone": time_zone} if start else {},
        "end": {"dateTime": end, "timeZone": time_zone} if end else {},
        "location": location,
        "attendees": attendees,
        "colorId": color_id,
        "reminders": reminders,
        "recurrence": recurrence
    }
    event_body = {k: v for k, v in event_body.items() if v}
    created = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    return created


@mcp.tool(description="Update an existing calendar event with recurring event modification scope support.")
async def update_event(
        calendar_id: Annotated[
            str, Field(description="ID of the calendar (use 'primary' for the main calendar)")
        ] = "primary",
        event_id: Annotated[
            str, Field(description="ID of the event to update")
        ] = "",
        summary: Annotated[
            Optional[str], Field(description="Updated title of the event")
        ] = None,
        description: Annotated[
            Optional[str], Field(description="Updated description/notes")
        ] = None,
        start: Annotated[
            Optional[str], Field(description="Updated start time: '2024-01-01T10:00:00'")
        ] = None,
        end: Annotated[
            Optional[str], Field(description="Updated end time: '2024-01-01T11:00:00'")
        ] = None,
        time_zone: Annotated[
            Optional[str], Field(
                description="Updated timezone as IANA Time Zone Database name. If not provided, uses the calendar's default timezone.")
        ] = None,
        location: Annotated[
            Optional[str], Field(description="Updated location")
        ] = None,
        attendees: Annotated[
            Optional[List[dict]], Field(description="Updated attendee list")
        ] = None,
        color_id: Annotated[
            Optional[str], Field(description="Updated color ID")
        ] = None,
        reminders: Annotated[
            Optional[dict], Field(description="Reminder settings for the event")
        ] = None,
        recurrence: Annotated[
            Optional[List[str]], Field(description="Updated recurrence rules")
        ] = None,
        send_updates: Annotated[
            Optional[str], Field(description="Whether to send update notifications")
        ] = None,
        original_start_time: Annotated[
            Optional[str], Field(description="Original start time in the ISO 8601 format '2024-01-01T10:00:00'")
        ] = None
):
    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start, "timeZone": time_zone} if start else {},
        "end": {"dateTime": end, "timeZone": time_zone} if end else {},
        "location": location,
        "attendees": attendees,
        "colorId": color_id,
        "reminders": reminders,
        "recurrence": recurrence,
        "originalStartTime": {"dateTime": original_start_time, "timeZone": time_zone} if original_start_time else {},

    }
    event_body = {k: v for k, v in event_body.items() if v}
    updated = service.events().update(
        calendarId=calendar_id, eventId=event_id, body=event_body,
        sendUpdates=send_updates,
    ).execute()
    return updated


@mcp.tool(description="Delete a calendar event.")
async def delete_event(
        calendar_id: Annotated[
            str, Field(description="ID of the calendar (use 'primary' for the main calendar)")
        ] = "primary",
        event_id: Annotated[
            str, Field(description="ID of the event to delete")
        ] = "",
        send_updates: Annotated[
            Optional[str], Field(description="Whether to send cancellation notifications")
        ] = None
):
    if send_updates:
        service.events().delete(calendarId=calendar_id, eventId=event_id, sendUpdates=send_updates).execute()
    else:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {"status": "deleted"}


@mcp.tool(
    description="Query free/busy information for calendars. Note: Time range is limited to a maximum of 3 months between timeMin and timeMax.")
async def get_freebusy(
        calendars: Annotated[
            List[dict], Field(description="List of calendars and/or groups to query for free/busy information")
        ] = [],
        time_min: Annotated[
            str, Field(
                description="Start time boundary. Preferred: '2024-01-01T00:00:00' (uses timeZone parameter or calendar timezone). Also accepts: '2024-01-01T00:00:00Z' or '2024-01-01T00:00:00-08:00'.")
        ] = "",
        time_max: Annotated[
            str, Field(
                description="End time boundary. Preferred: '2024-01-01T23:59:59' (uses timeZone parameter or calendar timezone). Also accepts: '2024-01-01T23:59:59Z' or '2024-01-01T23:59:59-08:00'.")
        ] = "",
        time_zone: Annotated[
            Optional[str], Field(description="Timezone for the query")
        ] = None,
        group_expansion_max: Annotated[
            Optional[int], Field(description="Maximum number of calendars to expand per group (max 100)")
        ] = None,
        calendar_expansion_max: Annotated[
            Optional[int], Field(description="Maximum number of calendars to expand (max 50)")
        ] = None
):
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": calendars
    }
    if time_zone:
        body["timeZone"] = time_zone
    if group_expansion_max is not None:
        body["groupExpansionMax"] = group_expansion_max
    if calendar_expansion_max is not None:
        body["calendarExpansionMax"] = calendar_expansion_max

    result = service.freebusy().query(body=body).execute()
    return result.get("calendars", {})


@mcp.tool(description="List available color IDs and their meanings for calendar events")
async def list_colors():
    return service.colors().get().execute()


def main():
    mcp.run()


if __name__ == '__main__':
    main()
