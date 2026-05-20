from common.environment_variable import EnvironmentVariable
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from common.style import Colour
import os
import utils.date_utils as du
import utils.string_utils as su

import requests


class Match(object):
    def __init__(self, row, venue_collection):
        self.resources_folder = os.path.join(os.getcwd(), "biddenham_cricket_fixtures", "resources")
        self.template_folder = os.path.join(self.resources_folder, "template")
        self.data = row
        self.venue_collection = venue_collection
        self.get_data_from_row()
        self.exclude = self.check_for_exclusion()

    def write_event(self):
        if not self.exclude:
            self.get_api_credentials()
            self.get_venue_id()
            self.insert_event_via_api()

    def check_for_exclusion(self):
        excluded_strata = [
            "Biddenham CC - Under 9",
            "Biddenham CC - Under 11",
            "Biddenham CC - Under 11 B",
            "Biddenham CC - Under 13",
            "Biddenham CC - Under 13 B",
        ]
        if self.stratum in excluded_strata:
            return True
        return False

    def get_api_credentials(self):
        """
        Gets the credentials required to connect to the REST API
        """
        # Get cricket category
        self.CRICKET_CATEGORY_ID = EnvironmentVariable("CRICKET_CATEGORY_ID", "int", False).value

        # Get API username
        self.WORDPRESS_USERNAME = EnvironmentVariable("WORDPRESS_USERNAME", "string", False).value

        # Get API application key
        self.WORDPRESS_APPLICATION_KEY = EnvironmentVariable("WORDPRESS_APPLICATION_KEY", "string", False).value

        # Get the earliest date for events to be imported, to avoid importing old events that have already passed
        self.PETERS_PICTUREHOUSE_EARLIEST_DATE = EnvironmentVariable("PETERS_PICTUREHOUSE_EARLIEST_DATE", "date", False).value

        # Get the site URL for the API endpoint
        self.WORDPRESS_SITE_URL = EnvironmentVariable("WORDPRESS_SITE_URL", "string", False).value

        self.EVENTS_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"

    def get_venue_id(self):
        venue = self.venue_collection.venues_dict.get(self.venue, None)
        if venue:
            self.venue_id = venue.venue_id
        _ = 1

    def get_data_from_row(self):
        """
        Takes the row data passed into the class, and generates
        member variables from the cells.
        """
        self.stratum: str = self.data["stratum"]
        self.home_team: str = self.data["home team"]
        self.away_team: str = self.data["away team"]
        self.venue: str = self.data["venue"]
        self.date_string: str = self.data["date"]
        self.date: datetime = self.cricket_date_to_actual_date(self.date_string)
        self.time: str = self.data["time"]
        self.venue_id: int = None
        self.get_time_start_and_end()
        self.get_competition()
        _ = 1

    def get_time_start_and_end(self):
        """
        Gets the start and end time for the event, based on the time string in the data.
        This is required for the API, which needs a start and end time.
        """
        time_start = self.time + ":00"
        time_start_obj = datetime.strptime(time_start, "%H:%M:%S")

        # Add 4 hours
        time_end_obj = time_start_obj + timedelta(hours=3)

        # Convert back to a string in the same format
        # time_end = time_end_obj.strftime("%H:%M:%S")
        date_start = datetime.combine(self.date, time_start_obj.time())
        date_end = datetime.combine(self.date, time_end_obj.time())

        self.date_start = date_start.strftime("%Y-%m-%d %H:%M:%S")
        self.date_end = date_end.strftime("%Y-%m-%d %H:%M:%S")
        _ = 1

    def get_competition(self):
        competitions = {
            "Biddenham CC - Sunday League XI": "Cricket Sunday League XI",
            "Biddenham CC - Sunday Friendly XI": "Cricket Sunday Friendly XI",
            "Biddenham CC - Midweek XI": "Cricket Midweek XI",
            "Biddenham CC - Under 9": "Cricket Under 9",
            "Biddenham CC - Under 11": "Cricket Under 11",
            "Biddenham CC - Under 11 B": "Cricket Under 11 B",
            "Biddenham CC - Under 13": "Cricket Under 13",
            "Biddenham CC - Under 13 B": "Cricket Under 13 B",
            "Biddenham CC - Under 15": "Cricket Under 15",
        }
        self.competition = competitions.get(self.stratum, self.stratum)

    def get_date_string(self) -> None:
        """
        Gets the date in the valid format (Thursday, 13th July 2026)
        """
        if not self.is_valid_match():
            return
        dt = self.show_date
        day = dt.day
        suffix = du.get_day_suffix(day)
        self.date_formatted = dt.strftime(f"%A, {day}{suffix} %B %Y")

    def insert_event_via_api(self):
        """
        Get the template that contains the summary (body) of the event
        prior to insertion of data to replace placeholders
        """

        if self.event_exists(self.home_team, self.away_team, self.date):
            print(f"Skipping existing event {Colour.CYAN}{self.home_team} vs {self.away_team}{Colour.RESET} on {self.date_string}.")
            return

        print(f"Creating event {Colour.CYAN}{self.home_team} vs {self.away_team}{Colour.RESET} for {self.date_string}.")

        # Get the HTML template
        event_template: str = os.path.join(self.template_folder, "event_template.html.txt")

        # Open the template
        with open(event_template, "r", encoding="utf-8") as file:
            template_content = file.read()
            # Make replacements
            self.description = self.replace_placeholders(template_content)

            event_data = {
                "title": f" {self.competition}: {self.home_team} vs {self.away_team}",
                "description": self.description,
                "status": "publish",
                "start_date": self.date_start,
                "end_date": self.date_end,
                "cost": "0.00",
                "categories": [self.CRICKET_CATEGORY_ID],
                # "venue": 840,
                # "organizer": 4732,
                "show_map": True,
                "show_map_link": True,
            }

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

    def event_exists(self, home_team, away_team, date_obj):
        """
        Checks if an event with the same title exists on the same start date.
        start_date_obj should be a python date or datetime object.
        """
        home_team_sanitised = su.sanitise_string(self.home_team)
        away_team_sanitised = su.sanitise_string(self.away_team)
        # Create a window for the entire day
        day_start = date_obj.strftime("%Y-%m-%d 00:00:00")
        day_end = date_obj.strftime("%Y-%m-%d 23:59:59")

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
                if home_team_sanitised in wp_title and away_team_sanitised in wp_title:
                    return True

        return False

    def replace_placeholders(self, s):
        try:
            s = s.replace("{home_team}", self.home_team)
            s = s.replace("{away_team}", self.away_team)
            s = s.replace("{date_string}", self.date_string)
            s = s.replace("{time}", self.time)
            s = s.replace("{venue}", self.venue)
            s = s.replace("{venue_id}", str(self.venue_id))
            _ = 1
        except Exception as e:
            print(e)
            pass
        return s

    def cricket_date_to_actual_date(self, date_string):
        """
        Converts a date string in the format "Thursday 13th July 2026" to a datetime object.
        """
        try:
            date_format = "%A %d %B %Y"

            # Convert string to datetime object
            actual_date = datetime.strptime(date_string, date_format)
            return actual_date
        except Exception as e:
            print(f"Error parsing date: {e}")
            return None
