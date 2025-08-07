#!/usr/bin/env python3
"""
Basic usage example for the calendar-link package.
"""

from datetime import datetime
import pytz
from calendar_link import CalendarEvent, CalendarGenerator


def main():
    """Demonstrate basic usage of the calendar-link package."""
    
    print("=== Calendar Link Generator Demo ===\n")
    
    # Create a sample event
    event = CalendarEvent(
        title="Team Meeting",
        start_time=datetime(2024, 1, 15, 10, 0),  # 10:00 AM
        end_time=datetime(2024, 1, 15, 11, 0),    # 11:00 AM
        description="Weekly team sync meeting to discuss project progress",
        location="Conference Room A",
        attendees=["john@example.com", "jane@example.com", "bob@example.com"]
    )
    
    print(f"Event: {event.title}")
    print(f"Time: {event.start_time.strftime('%Y-%m-%d %H:%M')} - {event.end_time.strftime('%H:%M')}")
    print(f"Location: {event.location}")
    print(f"Duration: {event.get_duration_minutes()} minutes")
    print(f"Attendees: {', '.join(event.attendees)}")
    print()
    
    # Initialize generator
    generator = CalendarGenerator()
    
    # Generate links for different services
    services = ["google", "apple", "yahoo", "outlook", "office365"]
    
    print("=== Calendar Links ===")
    for service in services:
        try:
            link = generator.generate_link(event, service)
            print(f"{service.upper()}: {link}")
        except Exception as e:
            print(f"{service.upper()}: Error - {e}")
        print()
    
    # Generate ICS file
    print("=== ICS File Content ===")
    ics_content = generator.generate_ics(event)
    print(ics_content)
    
    # Save ICS file
    with open("team_meeting.ics", "w") as f:
        f.write(ics_content)
    print("\nICS file saved as 'team_meeting.ics'")
    
    # Generate all links at once
    print("\n=== All Links ===")
    all_links = generator.generate_all_links(event)
    for service, link in all_links.items():
        if service != "ics":
            print(f"{service}: {link}")
        else:
            print(f"{service}: [ICS content generated]")


def timezone_example():
    """Demonstrate timezone handling."""
    
    print("\n=== Timezone Example ===")
    
    # Create event with specific timezone
    ny_tz = pytz.timezone("America/New_York")
    start_time = ny_tz.localize(datetime(2024, 1, 15, 14, 30))  # 2:30 PM EST
    
    event = CalendarEvent(
        title="Client Call",
        start_time=start_time,
        end_time=start_time.replace(hour=15, minute=30),  # 3:30 PM EST
        description="Important client meeting",
        location="Virtual Meeting",
        timezone="America/New_York"
    )
    
    print(f"Event: {event.title}")
    print(f"Time (EST): {event.start_time.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Timezone: {event.timezone}")
    
    generator = CalendarGenerator()
    google_link = generator.generate_link(event, "google")
    print(f"Google Calendar Link: {google_link}")


def all_day_example():
    """Demonstrate all-day events."""
    
    print("\n=== All-Day Event Example ===")
    
    event = CalendarEvent(
        title="Company Holiday",
        start_time=datetime(2024, 1, 15, 0, 0),
        end_time=datetime(2024, 1, 15, 0, 0),
        description="Office closed for Martin Luther King Jr. Day",
        all_day=True
    )
    
    print(f"Event: {event.title}")
    print(f"Date: {event.start_time.strftime('%Y-%m-%d')}")
    print(f"All-day: {event.all_day}")
    
    generator = CalendarGenerator()
    google_link = generator.generate_link(event, "google")
    print(f"Google Calendar Link: {google_link}")


if __name__ == "__main__":
    main()
    timezone_example()
    all_day_example() 