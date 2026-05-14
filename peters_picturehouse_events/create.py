import requests
from requests.auth import HTTPBasicAuth
from common.environment_variable import EnvironmentVariable

# Configuration
PETERS_PICTUREHOUSE_USERNAME = EnvironmentVariable(
    "PETERS_PICTUREHOUSE_USERNAME", "string", False
).value
PETERS_PICTUREHOUSE_APPLICATION_KEY = EnvironmentVariable(
    "PETERS_PICTUREHOUSE_APPLICATION_KEY", "string", False
).value

SITE_URL = "https://biddenham.org.uk"
ENDPOINT = f"{SITE_URL}/wp-json/tribe/events/v1/events"


def event_exists(title, start_date):
    """
    Checks if an event with the same title exists on the same start date.
    """
    # The API uses 'start_date' as a filter to find events starting after/on a time
    # We fetch events for that specific day to narrow it down
    params = {"start_date": start_date, "per_page": 50}

    response = requests.get(
        ENDPOINT,
        params=params,
        auth=HTTPBasicAuth(
            PETERS_PICTUREHOUSE_USERNAME, PETERS_PICTUREHOUSE_APPLICATION_KEY
        ),
    )

    if response.status_code == 200:
        existing_events = response.json().get("events", [])
        for event in existing_events:
            # Check for exact title match and date match
            # Note: response dates are often in 'YYYY-MM-DD HH:MM:SS' format
            if event.get("title") == title and event.get("start_date") == start_date:
                return True
    return False


def create_wp_event():
    title = "My test event"
    start_date = "2027-01-13 19:30:00"

    # --- Duplicate Check ---
    if event_exists(title, start_date):
        print(f"Skipping: Event '{title}' already exists on {start_date}.")
        return

    description_html = """
<!-- wp:tribe/event-datetime {"className":"date icon"} /-->
<!-- wp:tribe/event-price {"className":"price icon"} /-->
<!-- wp:heading --><h2 class="wp-block-heading">About This Event</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>Generated directly from Python.</p><!-- /wp:paragraph -->
<!-- wp:tribe/event-venue /-->
"""

    event_data = {
        "title": title,
        "description": description_html,
        "status": "publish",
        "start_date": start_date,
        "end_date": "2027-01-13 21:30:00",
        "cost": "5.00",
        "venue": 840,
        "organizer": 4732,
        "show_map": True,
        "show_map_link": True,
    }

    print(f"Attempting to create event: {title}...")

    response = requests.post(
        ENDPOINT,
        json=event_data,
        auth=HTTPBasicAuth(
            PETERS_PICTUREHOUSE_USERNAME, PETERS_PICTUREHOUSE_APPLICATION_KEY
        ),
    )

    if response.status_code == 201:
        result = response.json()
        print(f"Successfully created event! ID: {result.get('id')}")
    else:
        print(f"Failed to create event. Status code: {response.status_code}")


if __name__ == "__main__":
    create_wp_event()
