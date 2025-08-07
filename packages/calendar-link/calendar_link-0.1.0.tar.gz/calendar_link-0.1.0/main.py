#!/usr/bin/env python3
"""
Main entry point for the calendar-link package demonstration.
"""

from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator


def main():
    """Demonstrate the calendar-link package."""
    print("Calendar Link Generator")
    print("=" * 30)
    
    # Create a sample event
    event = CalendarEvent(
        title="Sample Meeting",
        start_time=datetime(2024, 1, 15, 14, 0),  # 2:00 PM
        end_time=datetime(2024, 1, 15, 15, 0),    # 3:00 PM
        description="This is a sample meeting to demonstrate the calendar-link package",
        location="Virtual Meeting Room",
        attendees=["user@example.com"]
    )
    
    # Initialize generator
    generator = CalendarGenerator()
    
    # Generate Google Calendar link
    yahoo_link = generator.generate_link(event, "yahoo")
    print(f"Yahoo Calendar Link: {yahoo_link}")
    
    # Generate ICS content
    ics_content = generator.generate_ics(event)
    print(f"\nICS Content:\n{ics_content}")
    
    # Show supported services
    services = generator.get_supported_services()
    print(f"\nSupported Services: {list(services.keys())}")


if __name__ == "__main__":
    main()
