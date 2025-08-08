"""
ICS Calendar Utils - Python utility library for generating and manipulating ICS calendar files.

This library provides tools for processing events from various sources and generating
RFC 5545 compliant ICS calendar files.
"""

from .event_processor import EventProcessor
from .ics_generator import ICSGenerator

__version__ = "0.2.1"
__author__ = "ronschaeffer"
__all__ = ["EventProcessor", "ICSGenerator", "create_calendar", "process_and_generate"]


def create_calendar(
    events: list[dict],
    calendar_name: str = "Generated Calendar",
    filename: str | None = None,
    field_mapping: dict[str, str] | None = None,
) -> str:
    """
    Simple convenience function to create an ICS calendar from raw events.

    Args:
        events: List of raw event dictionaries
        calendar_name: Name for the calendar
        filename: Optional filename to save the ICS file
        field_mapping: Optional field mapping for event processing

    Returns:
        ICS calendar content as string

    Example:
        >>> events = [
        ...     {
        ...         'title': 'Team Meeting',
        ...         'date': '2024-12-20',
        ...         'time': '14:00',
        ...         'location': 'Conference Room A'
        ...     }
        ... ]
        >>> ics_content = create_calendar(events, "Work Calendar")
    """
    # Process events
    processor = EventProcessor()
    if field_mapping:
        processor.add_mapping(field_mapping)
    processed_events = processor.process_events(events)

    # Generate ICS
    generator = ICSGenerator(calendar_name=calendar_name)
    ics_content = generator.generate_ics(processed_events, filename=filename)

    return ics_content


def process_and_generate(
    events: list[dict],
    calendar_name: str = "Generated Calendar",
    output_file: str | None = None,
    field_mapping: dict[str, str] | None = None,
    validate: bool = True,
) -> dict:
    """
    Process events and generate ICS calendar with detailed results.

    Args:
        events: List of raw event dictionaries
        calendar_name: Name for the calendar
        output_file: Optional path to save the ICS file
        field_mapping: Optional field mapping for event processing
        validate: Whether to validate events before processing

    Returns:
        Dictionary containing:
        - 'ics_content': The generated ICS content
        - 'processed_events': List of processed events
        - 'processing_errors': List of processing errors
        - 'validation_errors': List of validation errors (if validate=True)
        - 'stats': Statistics about the processed events

    Example:
        >>> events = [
        ...     {'event_name': 'Concert', 'event_date': '2024-12-25', 'venue': 'Music Hall'}
        ... ]
        >>> result = process_and_generate(
        ...     events,
        ...     calendar_name="Music Events",
        ...     output_file="concerts.ics",
        ...     field_mapping={'event_name': 'summary', 'event_date': 'dtstart_date', 'venue': 'location'}
        ... )
        >>> print(f"Generated {result['stats']['total_events']} events")
    """
    # Initialize components
    processor = EventProcessor()
    if field_mapping:
        processor.add_mapping(field_mapping)
    generator = ICSGenerator(calendar_name=calendar_name)

    # Process events
    processed_events = processor.process_events(events)
    processing_errors = processor.get_processing_errors()

    # Validate if requested
    validation_errors = []
    if validate:
        validation_errors = generator.validate_events(processed_events)

    # Generate statistics
    stats = generator.get_ics_stats(processed_events)

    # Generate ICS content
    ics_content = generator.generate_ics(processed_events, filename=output_file)

    return {
        "ics_content": ics_content,
        "processed_events": processed_events,
        "processing_errors": processing_errors,
        "validation_errors": validation_errors,
        "stats": stats,
    }


# Version info
def get_version() -> str:
    """Get the current version of ics_calendar_utils."""
    return __version__
