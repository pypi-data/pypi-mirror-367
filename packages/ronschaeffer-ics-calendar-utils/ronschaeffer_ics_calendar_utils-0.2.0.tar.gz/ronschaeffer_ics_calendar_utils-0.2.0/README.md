# 📅 ICS Calendar Utils

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/ronschaeffer-ics-calendar-utils.svg)](https://badge.fury.io/py/ronschaeffer-ics-calendar-utils)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ronschaeffer/ics_calendar_utils/workflows/CI/badge.svg)](https://github.com/ronschaeffer/ics_calendar_utils/actions)

A Python library for processing events and generating ICS calendar files from various data sources.

## ✨ Features

- **Event Processing**: Normalize events from any source with customizable field mappings
- **Date/Time Parsing**: Handles various date and time formats including midnight support
- **Event Validation**: Data quality validation before calendar generation
- **Statistics & Analytics**: Event data insights and processing statistics
- **Error Handling**: Invalid data handling with detailed error reporting
- **ICS Generation**: RFC 5545 compliant ICS calendar files
- **Type Safety**: Python 3.10+ type hints for improved development experience

## 📦 Installation

```bash
pip install ronschaeffer-ics-calendar-utils
```

## 🚀 Usage

### Basic Usage

```python
from ics_calendar_utils import create_calendar

# Your event data from any source
events = [
    {
        'title': 'Team Meeting',
        'date': '2024-12-20',
        'time': '14:00',
        'location': 'Conference Room A',
        'description': 'Weekly team sync'
    },
    {
        'title': 'Project Deadline',
        'date': 'Dec 25, 2024',
        'location': 'Online'
    }
]

# Field mapping configuration
field_mapping = {
    'title': 'summary',
    'date': 'dtstart_date',
    'time': 'dtstart_time'
}

# Generate ICS calendar
ics_content = create_calendar(
    events,
    calendar_name="My Calendar",
    filename="my_events.ics",
    field_mapping=field_mapping
)

print("Calendar generated successfully!")
```

## ⚙️ Configuration

### Field Mapping

```python
from ics_calendar_utils import process_and_generate

# Events with custom field names
events = [
    {
        'event_name': 'Rugby Match: England vs Wales',
        'event_date': '2024-12-21',
        'kickoff_time': '15:00',
        'venue': 'Twickenham Stadium',
        'competition': 'Six Nations',
        'ticket_url': 'https://example.com/tickets'
    }
]

# Custom field mapping
field_mapping = {
    'event_name': 'summary',
    'event_date': 'dtstart_date',
    'kickoff_time': 'dtstart_time',
    'venue': 'location',
    'competition': 'categories',
    'ticket_url': 'url'
}

# Process with detailed results
result = process_and_generate(
    events,
    calendar_name="Rugby Fixtures",
    output_file="rugby_calendar.ics",
    field_mapping=field_mapping,
    validate=True
)

# Access processing statistics
print(f"Processed {result['stats']['total_events']} events")
print(f"Events with times: {result['stats']['events_with_time']}")
print(f"Date range: {result['stats']['date_range']['earliest']} to {result['stats']['date_range']['latest']}")

if result['processing_errors']:
    print("Processing errors:", result['processing_errors'])
```

### Direct API Access

```python
from ics_calendar_utils import EventProcessor, ICSGenerator

# Initialize components
processor = EventProcessor()
processor.add_mapping({
    'event_title': 'summary',
    'start_date': 'dtstart_date'
})

generator = ICSGenerator(calendar_name="Custom Calendar")

# Process events
processed_events = processor.process_events(raw_events)

# Validate before generation
validation_errors = generator.validate_events(processed_events)
if validation_errors:
    print("Validation issues:", validation_errors)

# Generate ICS content
ics_content = generator.generate_ics(processed_events)
```

## 🎯 Supported Formats

### Date Formats
- ISO format: `2024-12-20`
- US format: `Dec 20, 2024` or `December 20, 2024`
- European format: `20/12/2024` or `20 December 2024`
- Various separators: dots, slashes, spaces, hyphens

### Time Formats
- 24-hour: `14:30`, `09:00`
- 12-hour: `2:30pm`, `9am`, `noon`, `midnight`
- Special times: `noon`, `12 noon`, `midnight`, `12 midnight`
- Multiple times: `14:30 & 16:45`, `noon & midnight`
- Flexible separators and spacing

## 🔧 Error Handling

```python
result = process_and_generate(events, validate=True)

# Check for processing issues
if result['processing_errors']:
    print("Data processing issues:")
    for error in result['processing_errors']:
        print(f"  - {error}")

if result['validation_errors']:
    print("Validation issues:")
    for error in result['validation_errors']:
        print(f"  - {error}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=ics_calendar_utils

# Run specific test file
poetry run pytest tests/test_event_processor.py
```

### Code Quality

```bash
# Format code
poetry run ruff format

# Lint code
poetry run ruff check

# Fix auto-fixable issues
poetry run ruff check --fix
```

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ronschaeffer/ics-calendar-utils.git
cd ics-calendar-utils

# Install with Poetry
poetry install

# Install development dependencies
poetry install --with dev
```

### Project Structure

```
ics_calendar_utils/
├── src/ics_calendar_utils/    # Main package
│   ├── event_processor.py     # Event data normalization
│   ├── ics_generator.py       # ICS file generation
│   └── __init__.py           # Public API
├── tests/                    # Test suite
├── examples/                 # Usage examples
└── docs/                    # Documentation
```

## 📋 Examples

Check out the [`examples/`](examples/) directory for working examples:

- **Basic Usage**: Simple calendar generation
- **Processing Examples**: Custom field mapping and error handling
- **Rugby Fixtures**: Sports calendar example

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.
