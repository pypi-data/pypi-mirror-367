"""
ICS Calendar Generator

This module provides functionality to generate ICS calendar files from processed event data.
It handles event formatting, timezone management, and ICS file creation.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any


class ICSGenerator:
    """
    Generates ICS calendar files from processed event data.

    This class takes processed events (from EventProcessor) and creates
    properly formatted ICS calendar files suitable for import into
    calendar applications.
    """

    def __init__(
        self, calendar_name: str = "Generated Calendar", timezone: str = "UTC"
    ):
        """
        Initialize the ICS generator.

        Args:
            calendar_name: Name of the calendar to appear in ICS file
            timezone: Timezone for events (default: UTC)
        """
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.prodid = "-//ICS Calendar Utils//Event Calendar//EN"

    def generate_ics(
        self, events: list[dict[str, Any]], filename: str | None = None
    ) -> str:
        """
        Generate an ICS calendar from processed events.

        Args:
            events: List of processed events from EventProcessor
            filename: Optional filename to save ICS content to

        Returns:
            ICS calendar content as string
        """
        ics_lines = self._create_calendar_header()

        for event in events:
            event_lines = self._create_event_component(event)
            ics_lines.extend(event_lines)

        ics_lines.append("END:VCALENDAR")

        ics_content = "\r\n".join(ics_lines) + "\r\n"

        if filename:
            self._save_to_file(ics_content, filename)

        return ics_content

    def _create_calendar_header(self) -> list[str]:
        """Create the calendar header section."""
        return [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{self.prodid}",
            f"X-WR-CALNAME:{self.calendar_name}",
            "X-WR-TIMEZONE:Europe/London",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]

    def _create_event_component(self, event: dict[str, Any]) -> list[str]:
        """
        Create an individual event component for the ICS file.

        Args:
            event: Processed event dictionary

        Returns:
            List of ICS lines for this event
        """
        lines = ["BEGIN:VEVENT"]

        # Generate unique identifier
        uid = str(uuid.uuid4())
        lines.append(f"UID:{uid}")

        # Event timestamps
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTAMP:{dtstamp}")

        # Event start time
        if event.get("dtstart_date") and event.get("dtstart_time"):
            dtstart = self._format_datetime(
                event["dtstart_date"], event["dtstart_time"]
            )
            lines.append(f"DTSTART:{dtstart}")
        elif event.get("dtstart_date"):
            # All-day event
            date_only = event["dtstart_date"].replace("-", "")
            lines.append(f"DTSTART;VALUE=DATE:{date_only}")

        # Event end time
        if event.get("dtend_date") and event.get("dtend_time"):
            dtend = self._format_datetime(event["dtend_date"], event["dtend_time"])
            lines.append(f"DTEND:{dtend}")
        elif event.get("dtstart_date") and not event.get("dtend_date"):
            # Single day event - end same day
            if event.get("dtstart_time"):
                # Assume 2-hour duration if no end time
                dtend = self._add_duration(
                    event["dtstart_date"], event["dtstart_time"], 2
                )
                lines.append(f"DTEND:{dtend}")
            else:
                # All-day event - next day
                next_day = self._add_day(event["dtstart_date"])
                lines.append(f"DTEND;VALUE=DATE:{next_day.replace('-', '')}")

        # Event summary (title)
        if event.get("summary"):
            summary = self._escape_ics_text(event["summary"])
            lines.append(f"SUMMARY:{summary}")

        # Event description
        if event.get("description"):
            description = self._escape_ics_text(event["description"])
            lines.append(f"DESCRIPTION:{description}")

        # Event location
        if event.get("location"):
            location = self._escape_ics_text(event["location"])
            lines.append(f"LOCATION:{location}")

        # Event URL
        if event.get("url"):
            lines.append(f"URL:{event['url']}")

        # Event categories/tags
        if event.get("categories"):
            if isinstance(event["categories"], list):
                categories = ",".join(event["categories"])
            else:
                categories = str(event["categories"])
            lines.append(f"CATEGORIES:{categories}")

        lines.append("END:VEVENT")
        return lines

    def _format_datetime(self, date_str: str, time_str: str) -> str:
        """
        Format date and time into ICS datetime format.

        Args:
            date_str: Date string in YYYY-MM-DD format
            time_str: Time string in HH:MM format

        Returns:
            ICS datetime string in YYYYMMDDTHHMMSSZ format
        """
        try:
            date_part = date_str.replace("-", "")
            time_part = time_str.replace(":", "") + "00"  # Add seconds

            # For now, assume UTC timezone
            return f"{date_part}T{time_part}Z"
        except (AttributeError, ValueError):
            # Fallback to current time if parsing fails
            return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def _add_duration(self, date_str: str, time_str: str, hours: int) -> str:
        """
        Add duration to a datetime and return ICS format.

        Args:
            date_str: Date string in YYYY-MM-DD format
            time_str: Time string in HH:MM format
            hours: Hours to add

        Returns:
            ICS datetime string
        """
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            dt_end = dt + timedelta(hours=hours)
            return dt_end.strftime("%Y%m%dT%H%M%SZ")
        except ValueError:
            # Fallback
            return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def _add_day(self, date_str: str) -> str:
        """
        Add one day to a date string.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Next day in YYYY-MM-DD format
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            next_day = dt + timedelta(days=1)
            return next_day.strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    def _escape_ics_text(self, text: str) -> str:
        """
        Escape text for ICS format.

        Args:
            text: Raw text string

        Returns:
            Escaped text suitable for ICS
        """
        if not text:
            return ""

        # ICS escaping rules
        text = str(text)
        text = text.replace("\\", "\\\\")  # Escape backslashes first
        text = text.replace(";", "\\;")  # Escape semicolons
        text = text.replace(",", "\\,")  # Escape commas
        text = text.replace("\n", "\\n")  # Escape newlines
        text = text.replace("\r", "")  # Remove carriage returns

        return text

    def _save_to_file(self, content: str, filename: str) -> None:
        """
        Save ICS content to a file.

        Args:
            content: ICS calendar content
            filename: Path to save file
        """
        try:
            with open(filename, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        except OSError as e:
            raise OSError(f"Failed to save ICS file: {e}") from e

    def validate_events(self, events: list[dict[str, Any]]) -> list[str]:
        """
        Validate events before ICS generation.

        Args:
            events: List of events to validate

        Returns:
            List of validation errors
        """
        errors = []

        for i, event in enumerate(events):
            event_errors = []

            # Check required fields
            if not event.get("summary"):
                event_errors.append("Missing summary/title")

            if not event.get("dtstart_date"):
                event_errors.append("Missing start date")
            else:
                # Validate date format
                try:
                    datetime.strptime(event["dtstart_date"], "%Y-%m-%d")
                except ValueError:
                    event_errors.append(f"Invalid date format: {event['dtstart_date']}")

            # Validate time format if present
            if event.get("dtstart_time"):
                try:
                    datetime.strptime(event["dtstart_time"], "%H:%M")
                except ValueError:
                    event_errors.append(f"Invalid time format: {event['dtstart_time']}")

            if event_errors:
                errors.append(f"Event {i + 1}: {'; '.join(event_errors)}")

        return errors

    def get_ics_stats(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Get statistics about events for ICS generation.

        Args:
            events: List of events

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_events": len(events),
            "events_with_time": 0,
            "all_day_events": 0,
            "events_with_location": 0,
            "events_with_url": 0,
            "date_range": {"earliest": None, "latest": None},
        }

        dates = []

        for event in events:
            # Count events with time
            if event.get("dtstart_time"):
                stats["events_with_time"] += 1
            else:
                stats["all_day_events"] += 1

            # Count events with location
            if event.get("location"):
                stats["events_with_location"] += 1

            # Count events with URL
            if event.get("url"):
                stats["events_with_url"] += 1

            # Collect dates for range calculation
            if event.get("dtstart_date"):
                try:
                    date_obj = datetime.strptime(event["dtstart_date"], "%Y-%m-%d")
                    dates.append(date_obj)
                except ValueError:
                    pass

        # Calculate date range
        if dates:
            dates.sort()
            stats["date_range"]["earliest"] = dates[0].strftime("%Y-%m-%d")
            stats["date_range"]["latest"] = dates[-1].strftime("%Y-%m-%d")

        return stats
