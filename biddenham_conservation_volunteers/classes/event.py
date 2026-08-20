import os
import re
import requests
from requests.auth import HTTPBasicAuth
from common.style import Colour
from common.environment_variable import EnvironmentVariable
import utils.date_utils as du
import utils.string_utils as su


class Event:
    def __init__(self, row):
        self.date = su.standardise_whitespace(row.cells[0].text.strip())
        self.task_number = row.cells[1].text.strip()
        self.location = row.cells[2].text.strip()
        self.nature_of_task = row.cells[3].text.strip()
        self.start_time = row.cells[4].text.strip()
        self.end_time = row.cells[5].text.strip()
        self.leader = row.cells[6].text.strip()
        self.tools = row.cells[7].text.strip()

        self.event_start = du.parse_custom_datetime(self.date, self.start_time, is_start=True)
        self.event_end = du.parse_custom_datetime(self.date, self.end_time, is_start=False)

        self.event_start_string = du.date_to_wordpress_date_string(self.event_start)
        self.event_end_string = du.date_to_wordpress_date_string(self.event_end)

        self.day_start = du.parse_custom_datetime(self.date, "00:00", is_start=True)
        self.day_end = du.parse_custom_datetime(self.date, "23:59", is_start=False)

        self.template_folder = os.path.join(os.getcwd(), "biddenham_conservation_volunteers", "resources", "templates")
        _ = 1

        # Format location
        self.format_location()

        # This will be both the nature_of_task in the body and in the title of the event
        self.format_nature_of_task()

        # This will be the title of the event
        self.format_title()

        # This is what is noted about tools
        self.format_tools()

    def format_location(self):
        self.location = self.location.replace("Cowslip", "Cowslip Meadow")
        self.location = self.location.replace("Cowslip Meadow Meadow", "Cowslip Meadow")
        self.location = self.location.replace("FP", "Footpath")
        self.location = self.location.replace("&", "and")
        self.is_footpath = "footpath" in self.location.lower()

    def format_nature_of_task(self):
        self.nature_of_task = self.nature_of_task.replace("Watering ", "Watering of ")
        self.nature_of_task = self.nature_of_task.replace("Watering of of ", "Watering of ")
        self.nature_of_task = self.nature_of_task.replace("Remove Blackthorn", "Blackthorn removal")

    def format_title(self):
        if self.nature_of_task == "Footpath cut back":
            self.is_footpath = True
            footpath_string = "footpaths" if "and" in self.location else "footpath"
            self.title = f"Cut back of {footpath_string} {self.location}"
        else:
            self.is_footpath = False
            self.title = f"{self.nature_of_task} at {self.location}"

        self.title = self.title.replace("footpath Footpath", "footpath")
        self.title = self.title.replace("footpaths Footpaths", "footpaths")
        self.title = f"Biddenham Conservation Volunteers - {self.title}"
        self.nature_of_task = self.nature_of_task.lower()
        self.location = self.location.replace("Footpath", "footpath")

    def format_tools(self):
        self.tools = self.tools.lower()
        self.tools = self.tools.replace("clip boards", "clipboards")
        if "tools in shed" in self.tools.lower():
            self.tools = self.tools.replace("tools in shed", "")
            self.tools = self.tools.strip()
            self.tools = self.tools.strip(",")
            self.tools = self.tools.strip()
            self.tools += ". Tools are available in the shed"

        if "tools and clipboards in shed" in self.tools.lower():
            self.tools = self.tools.replace("tools and clipboards in shed", "")
            self.tools = self.tools.strip()
            self.tools = self.tools.strip(",")
            self.tools = self.tools.strip()
            self.tools += ". Tools and clipboards are available in the shed"

        parts = [part.strip() for part in self.tools.split(".")]
        part_zero_parts = [part.strip() for part in parts[0].split(",")]
        parts[0] = su.list_to_sentence(part_zero_parts)
        self.tools = ". ".join(parts)

    def __repr__(self):
        return f"Task(date='{self.date}', task_number='{self.task_number}', location='{self.location}')"

    @property
    def prose_representation(self):
        template = "<img src='/wp-content/uploads/2025/06/conservation-volunteers-1024x285.webp' width='240' height='67' />"
        template += f"<p>On {self.date}, the Biddenham Conservation Volunteers will be carrying out {self.nature_of_task} at {self.location}. This will start at {self.start_time} and end at {self.end_time}. The session will be led by {self.leader}.</p>"
        if self.tools != "":
            template += f"<p>Please bring {self.tools}.</p>"
        template += "<p>We hope to see you there.</p>"
        template += "\n<p><a href='/biddenham-conservation-volunteers/'>Find out more about the work of the Biddenham Conservation Volunteers</a>"
        template += "\n<p>If you would like to join us, please contact Gilly Cowan, and she will send you further information.</p>"
        template += '\n<p class="email icon"><a href="mailto:gillycowan@btinternet.com">gillycowan@btinternet.com</a></p>'
        return template

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

        # Get the Events endpoint
        self.EVENTS_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"

        # Get the conservation category and organizer ID
        self.CONSERVATION_CATEGORY_ID = EnvironmentVariable("CONSERVATION_CATEGORY_ID", "string", False).value
        self.CONSERVATION_ORGANISER_ID = EnvironmentVariable("CONSERVATION_ORGANISER_ID", "string", False).value
        self.OVERWRITE_CONSERVATION_EVENTS = EnvironmentVariable("OVERWRITE_CONSERVATION_EVENTS", "boolean", False).value

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

    def insert_event_via_api(self):
        if self.event_start is None or self.event_end is None:
            return
        """
        Get the template that contains the summary (body) of the event
        prior to insertion of data to replace placeholders
        """

        self.get_api_credentials()
        event_exists, event_id = self.event_exists()
        if event_exists:
            if self.OVERWRITE_CONSERVATION_EVENTS:
                # Delete the existing event if the overwrite switch is set to 'True'
                self.delete_event(event_id)
            else:
                print(f"Skipping existing event {Colour.CYAN}{self.title} {Colour.RESET} on {self.date}.")
                return

        print(f"Creating event {Colour.CYAN}{self.title}{Colour.RESET} for {self.date}.")

        # Get the HTML template
        event_template: str = os.path.join(self.template_folder, "event_template.html.txt")
        # print(f"event_template is {event_template}")

        # Open the template
        with open(event_template, "r", encoding="utf-8") as file:
            template_content = file.read()
            # Make replacements
            self.description = self.replace_placeholders(template_content)

            # We are not going to use event venues!
            event_data = {
                "title": self.title,
                "description": self.description,
                "status": "publish",
                "start_date": self.event_start_string,
                "end_date": self.event_end_string,
                "cost": "0.00",
                "categories": [self.CONSERVATION_CATEGORY_ID],
                # "venue": 840,
                "organizer": self.CONSERVATION_ORGANISER_ID,
                "show_map": False,
                "show_map_link": False,
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
                _ = 1
                # result = response.json()
                # print(f"{Colour.GREEN}Successfully created event! ID: {result.get('id')}{Colour.RESET}\n")
            else:
                print(f"Failed to create event. Status code: {response.status_code}")

    def replace_placeholders(self, s):
        _ = 1
        try:
            s = s.replace("{date}", self.date)
            s = s.replace("{start_time}", self.start_time)
            s = s.replace("{end_time}", self.end_time)
            s = s.replace("{nature_of_task}", self.nature_of_task)
            s = s.replace("{location}", self.location)
            s = s.replace("{leader}", self.leader)
            s = s.replace("{tools}", self.tools)
            preposition = "of" if self.is_footpath else "at"
            s = s.replace("{preposition}", preposition)

            # Replace the image, depending on the location
            if "cowslip" in self.location.lower():
                image_filename = "bcv-event-cowslip.webp"
            elif "footpath" in self.location.lower():
                image_filename = "bcv-event-footpaths.webp"
            else:
                image_filename = "bcv-event-other.webp"
            s = s.replace("{image_filename}", image_filename)

            # Work out whether to include the tools section
            if self.tools is None:
                # Define a pattern that captures the entire block including the if tags
                # \s* handles any leading/trailing whitespace or newlines around the tags
                pattern = r"<!--\s*if:tools\s*-->.*?<!--\s*/if:tools\s*-->"

                # Replace the entire block with an empty string
                # re.DOTALL makes the '.' special character match newlines as well
                s = re.sub(pattern, "", s, flags=re.DOTALL)
            else:
                # If tools exist, you can strip the if tags and format the placeholder
                # This replaces the tags and injects the value into {tools}
                s = s.replace("<!-- if:tools -->", "")
                s = s.replace("<!-- /if:tools -->", "")
                s = s.format(tools=self.tools)

            # Work out whether to include the footpaths section
            if self.footpaths is None:
                # Define a pattern that captures the entire block including the if tags
                # \s* handles any leading/trailing whitespace or newlines around the tags
                pattern = r"<!--\s*if:footpaths\s*-->.*?<!--\s*/if:footpaths\s*-->"

                # Replace the entire block with an empty string
                # re.DOTALL makes the '.' special character match newlines as well
                s = re.sub(pattern, "", s, flags=re.DOTALL)

            _ = 1
        except Exception as _:
            # print(_)
            pass
        return s

    def event_exists(self):
        """
        Checks if an event with the same title exists on the same start date.
        start_date_obj should be a python date or datetime object.
        """
        title_sanitised = su.sanitise_string(self.title)
        params = {"start_date": self.day_start, "end_date": self.day_end, "per_page": 50}

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
