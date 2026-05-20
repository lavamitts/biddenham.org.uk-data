from common.environment_variable import EnvironmentVariable
from common.style import Colour
from datetime import datetime
from requests.auth import HTTPBasicAuth
import calendar
import os
import requests
import sys
import utils.date_utils as du
import utils.string_utils as su


class Event(object):
    def __init__(self, schedule_type, event_date, event_month, event_year, config):
        self.schedule_type = schedule_type

        # All fields where the scheduling type does not matter
        self.venue_id = config["venue_id"]
        self.venue = config["venue"]
        self.organiser_id = config.get("organiser_id", None)
        self.category_id = config.get("category_id", None)
        self.template_filename = config["template_filename"]
        self.cost = config["cost"]

        # All fields where the scheduling type does matter
        if self.schedule_type == "schedule":
            # We are in a monthly schedule
            self.event_date = event_date
            self.event_month = event_month
            self.event_year = event_year
            self.event_month_name = calendar.month_name[event_month]
            self.start_time = config["start_time"]
            self.end_time = config["end_time"]
            # Get all date and time variants needed later
            self.event_date_string = du.date_to_simple_date_string(self.event_date)
            self.get_time_start_and_end()

        elif self.schedule_type == "specific":
            # We have specific dates
            self.date_start = event_date[0]
            self.date_end = event_date[1]
            self.event_month_name = self.date_start.strftime("%B")
            self.event_year = self.date_start.strftime("%Y")
            self.event_date = self.date_start.date()
            self.event_date_string = self.date_start.strftime("%-d %B %Y")

            self.date_start = self.date_start.strftime("%Y-%m-%d %H:%M:%S")
            self.date_end = self.date_end.strftime("%Y-%m-%d %H:%M:%S")
            _ = 1

        # Get the full title
        self.title = config["title"]
        self.title = self.title.replace("{month}", self.event_month_name)
        self.title = self.title.replace("{year}", str(self.event_year))

        self.get_api_credentials()
        _ = 1

    def get_time_start_and_end(self):
        """
        Gets the start and end time for the event, based on the time string in the data.
        This is required for the API, which needs a start and end time.
        """
        # Start time
        time_start = self.start_time + ":00"
        time_start_obj = datetime.strptime(time_start, "%H:%M:%S")

        # End time
        time_end = self.end_time + ":00"
        time_end_obj = datetime.strptime(time_end, "%H:%M:%S")

        # Convert back to a string in the same format
        date_start = datetime.combine(self.event_date, time_start_obj.time())
        date_end = datetime.combine(self.event_date, time_end_obj.time())

        self.date_start = date_start.strftime("%Y-%m-%d %H:%M:%S")
        self.date_end = date_end.strftime("%Y-%m-%d %H:%M:%S")

    def get_api_credentials(self):
        """
        Gets the credentials required to connect to the REST API
        """
        # Get API username
        self.WORDPRESS_USERNAME = EnvironmentVariable("WORDPRESS_USERNAME", "string", False).value

        # Get API application key
        self.WORDPRESS_APPLICATION_KEY = EnvironmentVariable("WORDPRESS_APPLICATION_KEY", "string", False).value

        # Get the site URL for the API endpoint
        self.WORDPRESS_SITE_URL = EnvironmentVariable("WORDPRESS_SITE_URL", "string", False).value

        self.EVENTS_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"
        self.OVERWRITE_GENERIC_EVENTS = EnvironmentVariable("OVERWRITE_GENERIC_EVENTS", "string", False).value

    def event_exists(self):
        """
        Checks if an event with the same title exists on the same start date.
        start_date_obj should be a python date or datetime object.
        """
        title_sanitised = su.sanitise_string(self.title)
        # Create a window for the entire day
        day_start = self.event_date.strftime("%Y-%m-%d 00:00:00")
        day_end = self.event_date.strftime("%Y-%m-%d 23:59:59")

        params = {"start_date": day_start, "end_date": day_end, "per_page": 50}

        response = requests.get(
            self.EVENTS_ENDPOINT,
            params=params,
            auth=HTTPBasicAuth(
                self.WORDPRESS_USERNAME,
                self.WORDPRESS_APPLICATION_KEY,
            ),
        )

        if response.status_code == 200:
            existing_events = response.json().get("events", [])

            # Now we look for the specific title match within that day
            for event in existing_events:
                wp_title = event.get("title", "")
                wp_title = su.sanitise_string(wp_title)
                if title_sanitised in wp_title:
                    return True, event["id"]

        return False, None

    def generate_wordpress_event(self):
        proceed = True
        if not self.OVERWRITE_GENERIC_EVENTS:
            event_exists, _ = self.event_exists()
            if event_exists:
                proceed = False
        else:
            event_exists, existing_event_id = self.event_exists()
            if event_exists:
                self.delete_event(existing_event_id)

        if not proceed:
            return
        _ = 1

        print(f"Creating event {Colour.CYAN}{self.title}{Colour.RESET} for {Colour.CYAN}{self.event_date_string}{Colour.RESET}.")
        self.get_template()
        self.replace_placeholders()
        event_data = {
            "title": self.title,
            "description": self.description,
            "status": "publish",
            "start_date": self.date_start,
            "end_date": self.date_end,
            "cost": self.cost,
        }

        # Populate category-related fields
        if self.category_id:
            event_data["categories"] = [self.category_id]

        # Populate venue-related fields
        if self.venue_id:
            event_data["venue"] = self.venue_id
            event_data["show_map"] = True
            event_data["show_map_link"] = True
        else:
            event_data["show_map"] = False
            event_data["show_map_link"] = False

        # Populate organizer-related fields
        if self.organiser_id:
            event_data["organizer"] = self.organiser_id

        response = requests.post(
            self.EVENTS_ENDPOINT,
            json=event_data,
            auth=HTTPBasicAuth(
                self.WORDPRESS_USERNAME,
                self.WORDPRESS_APPLICATION_KEY,
            ),
        )

        if response.status_code == 201:
            result = response.json()
            print(f"{Colour.GREEN}Successfully created event! ID: {result.get('id')}{Colour.RESET}\n")
        else:
            print(f"Failed to create event. Status code: {response.status_code}")

    def get_template(self):
        self.template_content: str = ""
        self.resources_folder = os.path.join(os.getcwd(), "event_builder", "resources")
        self.template_folder = os.path.join(self.resources_folder, "templates")
        self.template_file = os.path.join(self.template_folder, self.template_filename)
        try:
            with open(self.template_file, "r", encoding="utf-8") as file:
                self.template_content = file.read()
        except Exception as _:
            print(f"There has been a problem opening the template file: {self.template_filename}")

    def replace_placeholders(self):
        s = self.template_content
        try:
            s = s.replace("{date_string}", self.event_date_string)
            # s = s.replace("{time}", self.time)
            s = s.replace("{venue}", self.venue)
            s = s.replace("{venue_id}", str(self.venue_id))
            _ = 1
        except Exception as e:
            print(e)
            sys.exit()
        self.description = s

    def delete_event(self, event_id):
        self.get_api_credentials()
        endpoint = f"{self.EVENTS_ENDPOINT}/{event_id}"

        # Set up basic authentication using your application password
        auth = HTTPBasicAuth(self.WORDPRESS_USERNAME, self.WORDPRESS_APPLICATION_KEY)

        # Optional parameters:
        # By default, WordPress moves items to the trash.
        # To delete it permanently, add 'force': 'true' to the parameters.
        params = {
            "force": "false"  # Change to "true" to bypass the trash entirely
        }

        try:
            # Send the DELETE request
            response = requests.delete(endpoint, auth=auth, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                # print(f"Success: Event {event_id} has been moved to the trash.")
                _ = 1
            elif response.status_code == 226:  # Status code for permanent deletion varies by setup, often 200
                # print(f"Success: Event {event_id} has been permanently deleted.")
                _ = 1
            else:
                print(f"Failed to delete event. Status code: {response.status_code}")
                print(f"Response: {response.json()}")

        except requests.exceptions.RequestException as error:
            print(f"An error occurred: {error}")
        _ = 1
