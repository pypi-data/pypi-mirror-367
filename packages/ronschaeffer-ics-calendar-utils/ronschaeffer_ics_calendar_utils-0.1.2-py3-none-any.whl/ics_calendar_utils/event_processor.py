#!/usr/bin/env python3
"""
Event processing module for normalizing various event data formats.

This module provides intelligent parsing and normalization of event data
from different sources into a standardized format suitable for ICS generation.
"""

import re
from datetime import datetime
from typing import Any


class EventProcessor:
    """
    Processes and normalizes event data from various sources.

    Handles date/time parsing, venue normalization, and field mapping
    to prepare events for ICS calendar generation.
    """

    def __init__(self):
        """Initialize the event processor with default field mappings."""
        self.field_mappings = {
            "fixture": "summary",
            "start_time": "dtstart_time",
            "date": "dtstart_date",
            "crowd": "description",
            "venue": "location",
            "end_time": "dtend_time",
        }
        self.error_log = []

    def add_mapping(self, mappings: dict[str, str]) -> None:
        """
        Add or update field mappings for event processing.

        Args:
            mappings: Dictionary mapping source fields to ICS fields
        """
        self.field_mappings.update(mappings)

    def normalize_time(self, time_str: str | None) -> str | None:
        """
        Normalize time format, returning a list of sorted times.

        Handles various time formats like:
        - "15:30"
        - "3:30pm"
        - "15:30 & 17:45"
        - "TBC"

        Args:
            time_str: Raw time string from source data

        Returns:
            List of normalized time strings in 24-hour format, or None if invalid
        """
        if not time_str or time_str.lower() == "tbc":
            return None

        time_str = time_str.lower().replace("noon", "12:00pm")
        time_str = re.sub(r"\s*\(tbc\)", "", time_str, flags=re.IGNORECASE)
        time_str = time_str.replace(".", ":")
        time_str = time_str.replace(" and ", " & ")

        time_patterns = re.findall(
            r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b", time_str, re.IGNORECASE
        )
        if not time_patterns:
            self.error_log.append(f"No valid time patterns found in: '{time_str}'")
            return None

        def is_valid_time(hour: int, minute: int) -> bool:
            return 0 <= hour <= 23 and 0 <= minute <= 59

        def parse_single_time(
            time_part: str, shared_meridian: str | None = None
        ) -> str | None:
            time_part = time_part.strip().lower()
            meridian = shared_meridian

            if "pm" in time_part:
                meridian = "pm"
                time_part = time_part.replace("pm", "").strip()
            elif "am" in time_part:
                meridian = "am"
                time_part = time_part.replace("am", "").strip()

            try:
                if ":" in time_part:
                    hour_str, minute_str = time_part.split(":")
                    hour, minute = int(hour_str), int(minute_str)
                else:
                    hour, minute = int(time_part), 0

                # Convert to 24-hour format
                if meridian == "pm" and hour != 12:
                    hour += 12
                elif meridian == "am" and hour == 12:
                    hour = 0

                if not is_valid_time(hour, minute):
                    return None

                return f"{hour:02d}:{minute:02d}"
            except (ValueError, AttributeError):
                return None

        # Find the last meridian indicator to use as default
        last_meridian = None
        for t in reversed(time_patterns):
            if "am" in t:
                last_meridian = "am"
                break
            elif "pm" in t:
                last_meridian = "pm"
                break

        converted_times = []
        for time_pattern in time_patterns:
            parsed_time = parse_single_time(time_pattern, last_meridian)
            if parsed_time:
                converted_times.append(parsed_time)

        return sorted(converted_times)[0] if converted_times else None

    def normalize_date_range(self, date_str: str | None) -> str | None:
        """
        Normalizes a variety of date string formats to 'YYYY-MM-DD'.

        Handles date ranges by taking the start date.

        Args:
            date_str: Raw date string from source data

        Returns:
            ISO format date string (YYYY-MM-DD) or None if invalid
        """
        if not date_str or not isinstance(date_str, str):
            return None

        # Pre-process the string to handle various formats
        cleaned_str = date_str.lower()

        # Remove day names, ordinals, and 'weekend' markers
        cleaned_str = re.sub(
            r"\b(mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|wknd)\b",
            "",
            cleaned_str,
        ).strip()

        cleaned_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", cleaned_str)

        # Handle date ranges like '16/17 May 2025' by taking the first day part
        cleaned_str = re.sub(
            r"(\d{1,2})\s*/\s*\d{1,2}(\s+[a-zA-Z]+\s+\d{2,4})",
            r"\1\2",
            cleaned_str,
        )

        # Normalize separators to a single space, but keep commas for certain patterns
        # First handle dates like "Dec 20, 2024" by converting to "20 Dec 2024"
        comma_match = re.match(r"([a-z]+)\s+(\d{1,2}),\s+(\d{4})", cleaned_str)
        if comma_match:
            month, day, year = comma_match.groups()
            cleaned_str = f"{day} {month} {year}"
        else:
            cleaned_str = cleaned_str.replace(",", "")

        cleaned_str = cleaned_str.replace("-", " ").replace("/", " ").replace(".", " ")
        cleaned_str = re.sub(r"\s+", " ", cleaned_str).strip()

        # List of possible date formats
        patterns = [
            "%Y-%m-%d",  # ISO format: 2024-12-20
            "%d %B %Y",  # e.g., 16 may 2025, 20 December 2024
            "%d %b %Y",  # e.g., 16 aug 2025, 20 Dec 2024
            "%d %B %y",  # e.g., 16 may 23
            "%d %b %y",  # e.g., 16 aug 23
            "%d %m %Y",  # e.g., 16 05 2025, 20 12 2024
            "%d %m %y",  # e.g., 16 05 23
            "%Y %m %d",  # ISO format with spaces
            "%b %d %Y",  # e.g., Dec 20, 2024
            "%B %d %Y",  # e.g., December 20, 2024
            "%m %d %Y",  # e.g., 12 20 2024
        ]

        for fmt in patterns:
            try:
                parsed_date = datetime.strptime(cleaned_str, fmt).date()
                # Handle 2-digit years
                if parsed_date.year < 2000:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        self.error_log.append(f"Failed to parse date: '{date_str}'")
        return None

    def process_events(self, raw_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Process a list of raw events into normalized format.

        Args:
            raw_events: List of raw event dictionaries from various sources

        Returns:
            List of normalized event dictionaries ready for ICS generation
        """
        self.error_log.clear()
        processed_events = []

        for i, raw_event in enumerate(raw_events):
            try:
                processed_event = self._process_single_event(raw_event)
                if processed_event:
                    processed_events.append(processed_event)
            except Exception as e:
                self.error_log.append(f"Error processing event {i}: {e}")

        return processed_events

    def _process_single_event(self, raw_event: dict[str, Any]) -> dict[str, Any] | None:
        """Process a single raw event into normalized format."""
        processed = {}

        # Map fields according to configured mappings
        for source_field, target_field in self.field_mappings.items():
            if source_field in raw_event and raw_event[source_field] is not None:
                value = raw_event[source_field]

                # Special processing for different field types
                if target_field == "dtstart_date":
                    value = self.normalize_date_range(value)
                    if not value:
                        return None  # Skip events with invalid dates
                elif target_field == "dtstart_time" or target_field == "dtend_time":
                    value = self.normalize_time(value)
                    if not value:
                        continue  # Skip this field if time is invalid

                processed[target_field] = value

        # Ensure we have required fields
        if "summary" not in processed:
            processed["summary"] = raw_event.get("fixture", "Untitled Event")

        return processed

    def get_processing_errors(self) -> list[str]:
        """Return any errors that occurred during processing."""
        return self.error_log.copy()
