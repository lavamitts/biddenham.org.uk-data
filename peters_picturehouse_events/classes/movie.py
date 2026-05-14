from common.environment_variable import EnvironmentVariable
from datetime import date
from requests.auth import HTTPBasicAuth
import base64
import os
import peters_picturehouse_events.utils.date_utils as du
import peters_picturehouse_events.utils.string_utils as su
import peters_picturehouse_events.utils.file_utils as fu
import requests


class Movie(object):
    def __init__(self, row):
        self.resources_folder = os.path.join(os.getcwd(), "peters_picturehouse_events", "resources")
        self.template_folder = os.path.join(self.resources_folder, "template")
        self.output_folder = os.path.join(self.resources_folder, "output")
        self.listing_folder = os.path.join(self.output_folder, "listing")

        # Make folders if they don't exist
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.listing_folder, exist_ok=True)

        self.get_api_credentials()

        self.data = row
        self.get_data_from_excel_row()
        self.get_date_string()
        if self.is_valid_movie():
            if not self.precedes_earliest_date():
                self.insert_event_via_api()

            self.generate_listing()

    def get_api_credentials(self):
        """
        Gets the creadentials required to connect to the REST API
        """
        # Get API username
        self.PETERS_PICTUREHOUSE_USERNAME = EnvironmentVariable("PETERS_PICTUREHOUSE_USERNAME", "string", False).value

        # Get API application key
        self.PETERS_PICTUREHOUSE_APPLICATION_KEY = EnvironmentVariable("PETERS_PICTUREHOUSE_APPLICATION_KEY", "string", False).value

        # Get the earliest date for events to be imported, to avoid importing old events that have already passed
        self.PETERS_PICTUREHOUSE_EARLIEST_DATE = EnvironmentVariable("PETERS_PICTUREHOUSE_EARLIEST_DATE", "date", False).value

        # Get the site URL for the API endpoint
        self.PETERS_PICTUREHOUSE_SITE_URL = EnvironmentVariable("PETERS_PICTUREHOUSE_SITE_URL", "string", False).value

        # Get the folder where movie images are stored
        self.MOVIE_IMAGE_FOLDER = EnvironmentVariable("MOVIE_IMAGE_FOLDER", "string", False).value

        self.EVENTS_ENDPOINT = f"{self.PETERS_PICTUREHOUSE_SITE_URL}/wp-json/tribe/events/v1/events"
        self.MEDIA_ENDPOINT = f"{self.PETERS_PICTUREHOUSE_SITE_URL}/wp-json/wp/v2/media"

    def get_data_from_excel_row(self):
        """
        Takes the row data passed into the class, and generates
        member variables from the cells.
        """
        self.show_date: date = self.data[0].date()
        self.show_date_string: str = self.data[0].date().isoformat()
        self.show_year: str = str(self.show_date.year)
        self.title: str = self.data[1]
        self.title_sanitised: str = su.sanitise_string(self.title)
        self.imdb_link: str = self.data[2]
        self.summary: str = self.data[3]
        self.starring: str = self.data[4]
        self.certification: str = str(self.data[5])
        self.running_time: str = self.data[6]
        self.release_year: str = str(self.data[7])
        self.imported: bool = su.YN(str(self.data[9]))
        self.year_added: str = str(self.data[10]).strip()
        self.month_added: str = str(self.data[11]).strip()
        if self.month_added == "" or self.month_added is None:
            self.month_added = du.get_month_number()
        else:
            self.month_added = self.month_added.zfill(2)

    def get_date_string(self) -> None:
        """
        Gets the date in the valid format (Thursday, 13th July 2026)
        """
        if not self.is_valid_movie():
            return
        dt = self.show_date
        day = dt.day
        suffix = du.get_day_suffix(day)
        self.date_formatted = dt.strftime(f"%A, {day}{suffix} %B %Y")

    def is_valid_movie(self) -> bool:
        """
        Checks if this is a valid movie (has a title)
        so that we can skip over blank rows in the Excel sheet.

        Returns:
            bool: is movie valid (has a title)?
        """

        return self.title is not None and self.title != ""

    def precedes_earliest_date(self) -> bool:
        """
        Checks if the movie's show date is before the earliest date for importing events.
        This is to avoid importing old events that have already passed.

        Returns:
            bool: does the movie's show date precede the earliest date?
        """

        return self.show_date < self.PETERS_PICTUREHOUSE_EARLIEST_DATE

    def insert_event_via_api(self):
        """
        Get the template that contains the summary (body) of the event
        prior to insertion of data to replace placeholders
        """

        if self.event_exists(self.title, self.show_date):
            print(f"Skipping event {self.title} on {self.show_date_string}.")
            return

        # Check if the image exists in Wordpress before attempting to create the event
        image_exists_in_wordpress = self.check_image_exists_in_wordpress(f"{self.title_sanitised}")
        if not image_exists_in_wordpress:
            print(f"Image for '{self.title}' not found in Wordpress media library. Skipping event creation.")

            filename_to_find = f"{self.title_sanitised}.webp"
            success, filename = fu.find_file(self.MOVIE_IMAGE_FOLDER, filename_to_find)
            if success:
                print(f"Found image file for '{self.title}': {filename}")
                self.upload_to_wordpress(filename)
                self.month_added = du.get_month_number()
                self.year_added = du.get_year()
            else:
                print(f"File not found: {filename_to_find}")
                return

        print(f"Creating event '{self.title}' for {self.show_date}.")

        # Get the HTML template
        event_template: str = os.path.join(self.template_folder, "event_template.html.txt")

        # Open the template
        with open(event_template, "r", encoding="utf-8") as file:
            template_content = file.read()
            # Make replacements
            self.description = self.replace_placeholders(template_content)

            event_data = {
                "title": f"Peter's Picturehouse: {self.title}",
                "description": self.description,
                "status": "publish",
                "start_date": self.show_date.strftime("%Y-%m-%d 19:00:00"),
                "end_date": self.show_date.strftime("%Y-%m-%d 21:30:00"),
                "cost": "5.00",
                "venue": 840,
                "organizer": 4732,
                "show_map": True,
                "show_map_link": True,
            }

            response = requests.post(
                self.EVENTS_ENDPOINT,
                json=event_data,
                auth=HTTPBasicAuth(
                    self.PETERS_PICTUREHOUSE_USERNAME,
                    self.PETERS_PICTUREHOUSE_APPLICATION_KEY,
                ),
            )

            if response.status_code == 201:
                result = response.json()
                print(f"Successfully created event! ID: {result.get('id')}")
            else:
                print(f"Failed to create event. Status code: {response.status_code}")

    def event_exists(self, title, start_date_obj):
        """
        Checks if an event with the same title exists on the same start date.
        start_date_obj should be a python date or datetime object.
        """
        # Create a window for the entire day
        day_start = start_date_obj.strftime("%Y-%m-%d 00:00:00")
        day_end = start_date_obj.strftime("%Y-%m-%d 23:59:59")

        params = {"start_date": day_start, "end_date": day_end, "per_page": 50}

        response = requests.get(
            self.EVENTS_ENDPOINT,
            params=params,
            auth=HTTPBasicAuth(
                self.PETERS_PICTUREHOUSE_USERNAME,
                self.PETERS_PICTUREHOUSE_APPLICATION_KEY,
            ),
        )

        if response.status_code == 200:
            existing_events = response.json().get("events", [])

            # Now we look for the specific title match within that day
            for event in existing_events:
                if title.strip().lower() in event.get("title").strip().lower():
                    return True

        return False

    def generate_listing(self):
        self.filename_as_text = f"{self.title_sanitised}.html.txt"

        # Get the HTML templates
        # It's crucial that this remains with a .txt extension, as opening with a .html extension causes issues
        # probably due to Prettier changing small details of the file imperceptbly.
        html_listing_template: str = os.path.join(self.template_folder, "listing_template.html.txt")

        # Make the subfolders
        os.makedirs(os.path.join(self.listing_folder, self.show_year), exist_ok=True)

        # Get the filename for the new listing
        listing_filename: str = os.path.join(self.listing_folder, self.show_year, self.filename_as_text)

        # Open the template
        with open(html_listing_template, "r", encoding="utf-8") as file:
            template_content = file.read()

        # Make replacements
        self.listing_html = self.replace_placeholders(template_content)

        # Save the resultant files
        with open(listing_filename, "w", encoding="utf-8", newline="") as file:
            file.write(self.listing_html)

    def replace_placeholders(self, s):
        try:
            s = s.replace("{title}", self.title)
            s = s.replace("{year_added}", self.year_added)
            s = s.replace("{month_added}", self.month_added)
            s = s.replace("{title_formatted}", self.title_sanitised)
            s = s.replace("{imdb_link}", self.imdb_link)
            s = s.replace("{date_formatted}", self.date_formatted)
            s = s.replace("{certification}", self.certification)
            s = s.replace("{release_year}", self.release_year)
            s = s.replace("{summary}", self.summary)
            s = s.replace("{starring}", self.starring)
            s = s.replace("{running_time}", self.running_time)
        except Exception as e:
            print(e)
            pass
        return s

    def check_image_exists_in_wordpress(self, file_name):
        # Parameters to filter the search
        params = {"search": file_name, "per_page": 10}

        try:
            response = requests.get(self.MEDIA_ENDPOINT, auth=HTTPBasicAuth(self.PETERS_PICTUREHOUSE_USERNAME, self.PETERS_PICTUREHOUSE_APPLICATION_KEY), params=params)

            if response.status_code == 200:
                media_items = response.json()

                # Verify if the exact filename exists in the results
                for item in media_items:
                    source_url = item.get("source_url", "")
                    if file_name in source_url:
                        print(f"Match found: {source_url}")
                        return True

                print("No exact match found in the media library.")
                return False
            else:
                print(f"Failed to connect. Status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def upload_to_wordpress(self, path):
        credentials = f"{self.PETERS_PICTUREHOUSE_USERNAME}:{self.PETERS_PICTUREHOUSE_APPLICATION_KEY}"
        token = base64.b64encode(credentials.encode())
        headers = {
            "Authorization": f"Basic {token.decode('utf-8')}",
            "Content-Disposition": f"attachment; filename={os.path.basename(path)}",
            "Content-Type": "image/webp",  # Adjust based on your file type (e.g., image/png)
        }

        with open(path, "rb") as file:
            media_data = file.read()

        response = requests.post(self.MEDIA_ENDPOINT, headers=headers, data=media_data)

        if response.status_code == 201:
            print("Upload successful.")
            print(f"Image Link: {response.json()['source_url']}")
        else:
            print(f"Upload failed. Status code: {response.status_code}")
            print(response.json())
