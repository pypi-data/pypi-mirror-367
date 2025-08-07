#!/usr/bin/env python3
"""
Advanced usage examples for the calendar-link package.
"""

from datetime import datetime, timedelta
import pytz
from calendar_link import CalendarEvent, CalendarGenerator
from calendar_link.utils import parse_datetime, validate_email, sanitize_text


def recurring_event_example():
    """Example of creating events for recurring meetings."""
    
    print("=== Recurring Event Example ===")
    
    # Create a weekly team meeting
    event = CalendarEvent(
        title="Weekly Team Standup",
        start_time=datetime(2024, 1, 15, 9, 0),  # Monday 9 AM
        end_time=datetime(2024, 1, 15, 9, 30),   # 30 minutes
        description="Daily standup meeting to discuss progress and blockers",
        location="Zoom Meeting",
        attendees=["team@company.com"]
    )
    
    generator = CalendarGenerator()
    
    # Generate links for different days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for i, day in enumerate(days):
        # Adjust the date for each day of the week
        event_date = event.start_time + timedelta(days=i)
        event.start_time = event_date
        event.end_time = event_date + timedelta(minutes=30)
        
        google_link = generator.generate_link(event, "google")
        print(f"{day}: {google_link}")


def timezone_conversion_example():
    """Example of handling different timezones."""
    
    print("\n=== Timezone Conversion Example ===")
    
    # Create an event in New York timezone
    ny_tz = pytz.timezone("America/New_York")
    start_time = ny_tz.localize(datetime(2024, 1, 15, 14, 0))  # 2 PM EST
    
    event = CalendarEvent(
        title="International Client Meeting",
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        description="Meeting with international clients",
        location="Virtual Meeting",
        timezone="America/New_York"
    )
    
    print(f"Event in EST: {event.start_time.strftime('%Y-%m-%d %H:%M %Z')}")
    
    # Convert to different timezones
    timezones = ["America/Los_Angeles", "Europe/London", "Asia/Tokyo"]
    
    generator = CalendarGenerator()
    
    for tz in timezones:
        tz_obj = pytz.timezone(tz)
        local_time = event.start_time.astimezone(tz_obj)
        print(f"Event in {tz}: {local_time.strftime('%Y-%m-%d %H:%M %Z')}")
        
        # Generate link with local timezone
        event.timezone = tz
        link = generator.generate_link(event, "google")
        print(f"Google Calendar Link: {link}")


def event_validation_example():
    """Example of event validation and error handling."""
    
    print("\n=== Event Validation Example ===")
    
    from calendar_link.exceptions import InvalidEventDataError, UnsupportedCalendarServiceError
    
    # Test invalid events
    invalid_events = [
        {
            "title": "",  # Empty title
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(hours=1)
        },
        {
            "title": "Invalid Event",
            "start_time": datetime.now() + timedelta(hours=1),  # End before start
            "end_time": datetime.now()
        }
    ]
    
    for i, event_data in enumerate(invalid_events):
        try:
            event = CalendarEvent(**event_data)
            print(f"Event {i+1}: Valid")
        except InvalidEventDataError as e:
            print(f"Event {i+1}: Invalid - {e}")
    
    # Test unsupported service
    generator = CalendarGenerator()
    event = CalendarEvent(
        title="Test Event",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1)
    )
    
    try:
        link = generator.generate_link(event, "unsupported_service")
        print(f"Generated link: {link}")
    except UnsupportedCalendarServiceError as e:
        print(f"Service error: {e}")


def batch_event_generation():
    """Example of generating multiple events at once."""
    
    print("\n=== Batch Event Generation ===")
    
    # Create multiple events
    events_data = [
        {
            "title": "Morning Standup",
            "start_time": "2024-01-15T09:00:00",
            "end_time": "2024-01-15T09:15:00",
            "description": "Daily morning standup",
            "location": "Conference Room A"
        },
        {
            "title": "Lunch Break",
            "start_time": "2024-01-15T12:00:00",
            "end_time": "2024-01-15T13:00:00",
            "description": "Lunch break",
            "location": "Cafeteria"
        },
        {
            "title": "Project Review",
            "start_time": "2024-01-15T15:00:00",
            "end_time": "2024-01-15T16:00:00",
            "description": "Weekly project review meeting",
            "location": "Virtual Meeting"
        }
    ]
    
    generator = CalendarGenerator()
    
    for i, event_data in enumerate(events_data):
        event = CalendarEvent.from_dict(event_data)
        print(f"\nEvent {i+1}: {event.title}")
        
        # Generate Google Calendar link
        google_link = generator.generate_link(event, "google")
        print(f"Google Calendar: {google_link}")
        
        # Generate ICS file
        ics_filename = f"event_{i+1}.ics"
        with open(ics_filename, "w") as f:
            f.write(generator.generate_ics(event))
        print(f"ICS file saved: {ics_filename}")


def utility_functions_example():
    """Example of using utility functions."""
    
    print("\n=== Utility Functions Example ===")
    
    # Parse datetime with timezone
    dt_str = "2024-01-15 14:30:00"
    dt = parse_datetime(dt_str, "America/New_York")
    print(f"Parsed datetime: {dt}")
    
    # Validate emails
    emails = ["user@example.com", "invalid-email", "test@domain.co.uk"]
    for email in emails:
        is_valid = validate_email(email)
        print(f"Email '{email}' is valid: {is_valid}")
    
    # Sanitize text
    dirty_text = "Event\nDescription\nwith\nmultiple\nlines\nand    extra   spaces"
    clean_text = sanitize_text(dirty_text)
    print(f"Original text: {repr(dirty_text)}")
    print(f"Sanitized text: {repr(clean_text)}")


def main():
    """Run all advanced examples."""
    print("Advanced Calendar Link Generator Examples")
    print("=" * 50)
    
    recurring_event_example()
    timezone_conversion_example()
    event_validation_example()
    batch_event_generation()
    utility_functions_example()


if __name__ == "__main__":
    main() 