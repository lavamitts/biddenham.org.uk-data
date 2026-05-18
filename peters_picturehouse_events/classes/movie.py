from common.environment_variable import EnvironmentVariable
from datetime import date
from requests.auth import HTTPBasicAuth
from common.style import Colour
import base64
import os
import utils.date_utils as du
import utils.string_utils as su
import utils.file_utils as fu
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
                self.insert_movie_via_api()

            self.generate_listing()

    def get_api_credentials(self):
        """
        Gets the credentials required to connect to the REST API
        """
        # Get API username
        self.WORDPRESS_USERNAME = EnvironmentVariable("WORDPRESS_USERNAME", "string", False).value

        # Get API application key
        self.WORDPRESS_APPLICATION_KEY = EnvironmentVariable("WORDPRESS_APPLICATION_KEY", "string", False).value

        # Get the earliest date for events to be imported, to avoid importing old events that have already passed
        self.PETERS_PICTUREHOUSE_EARLIEST_DATE = EnvironmentVariable("PETERS_PICTUREHOUSE_EARLIEST_DATE", "date", False).value

        # Get the site URL for the API endpoint
        self.WORDPRESS_SITE_URL = EnvironmentVariable("WORDPRESS_SITE_URL", "string", False).value

        # Get the folder where movie images are stored
        self.MOVIE_IMAGE_FOLDER = EnvironmentVariable("MOVIE_IMAGE_FOLDER", "string", False).value

        self.EVENTS_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"
        self.MEDIA_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/wp/v2/media"
        self.MOVIES_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/wp/v2/movies"

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
            print(f"Skipping existing event {Colour.CYAN}{self.title}{Colour.RESET} on {self.show_date_string}.")
            return

        # Check if the image exists in Wordpress before attempting to create the event
        image_exists_in_wordpress, image_id = self.check_image_exists_in_wordpress(f"{self.title_sanitised}")
        if not image_exists_in_wordpress:
            print(f"Image for {Colour.CYAN}{self.title}{Colour.RESET} not found in Wordpress media library. Searching locally ...")

            filename_to_find = f"{self.title_sanitised}.webp"
            success, filename = fu.find_file(self.MOVIE_IMAGE_FOLDER, filename_to_find)
            if success:
                # print(f"Found image file for '{self.title}': {filename}")
                self.upload_to_wordpress(filename)
                self.month_added = du.get_month_number()
                self.year_added = du.get_year()
                print(f"Uploading image for movie {Colour.GREEN}{self.title}{Colour.RESET} to Wordpress media library ...")
            else:
                print(f"\nImage file for movie {Colour.RED}{self.title}{Colour.RESET} not found. Please create an image for this movie before retrying.")
                return

        print(f"Creating event {Colour.CYAN}{self.title}{Colour.RESET} for {self.show_date}.")

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
                "categories": [70],
                "venue": 840,
                "organizer": 4732,
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

    def insert_movie_via_api(self):
        """
        Inserts a movie into the 'Movies' Custom Post Type with ACF fields.
        Assumes self.image_id is set after uploading the media.
        """

        # Only write to WordPress if the WRITE_MOVIES_DIRECTLY_TO_WP environment variable is set to True
        WRITE_MOVIES_DIRECTLY_TO_WP = EnvironmentVariable("WRITE_MOVIES_DIRECTLY_TO_WP", "bool", False).value
        if not WRITE_MOVIES_DIRECTLY_TO_WP:
            return

        if self.movie_exists(self.title, self.show_date):
            print(f"Skipping existing movie {Colour.CYAN}{self.title}{Colour.RESET}.")
            return

        # Handle image upload as you did in your previous function
        # Assuming self.upload_to_wordpress sets self.image_id
        image_exists_in_wordpress, self.image_id = self.check_image_exists_in_wordpress(f"{self.title_sanitised}")

        if not image_exists_in_wordpress:
            filename_to_find = f"{self.title_sanitised}.webp"
            success, filename = fu.find_file(self.MOVIE_IMAGE_FOLDER, filename_to_find)
            if success:
                media_result = self.upload_to_wordpress(filename)
                # Make sure your upload function returns the ID of the uploaded image
                self.image_id = media_result.get("id")
            else:
                print(f"Image for {self.title} not found locally.")
                return

        # Prepare the movie data
        movie_data = {
            "title": self.title,
            "content": self.summary,  # This goes into the main body editor
            "status": "publish",
            "featured_media": self.image_id,  # Sets the Featured Image
            # This nested 'acf' dictionary is what populates your custom fields
            "acf": {
                "date": self.show_date.strftime("%Y%m%d"),
                # "date": self.show_date.strftime("%Y-%m-%d"),
                "imdb_link": self.imdb_link,
                "starring": self.starring,
                "certification": self.certification,
                "running_time": self.running_time,
                "release_year": self.release_year,
            },
        }

        # Ensure MOVIES_ENDPOINT is something like:
        # https://your-site.com/wp-json/wp/v2/movies
        response = requests.post(
            self.MOVIES_ENDPOINT,
            json=movie_data,
            auth=HTTPBasicAuth(
                self.WORDPRESS_USERNAME,
                self.WORDPRESS_APPLICATION_KEY,
            ),
        )

        if response.status_code == 201:
            print(f"{Colour.GREEN}Successfully created Movie: {self.title}{Colour.RESET}")
        else:
            print(f"Failed to create movie. Status code: {response.status_code}")
            print(response.text)

    def event_exists(self, title, start_date_obj):
        """
        Checks if an event with the same title exists on the same start date.
        start_date_obj should be a python date or datetime object.
        """
        title_sanitised = su.sanitise_string(self.title)
        # Create a window for the entire day
        day_start = start_date_obj.strftime("%Y-%m-%d 00:00:00")
        day_end = start_date_obj.strftime("%Y-%m-%d 23:59:59")

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
                    return True

        return False

    def movie_exists(self, title, show_date_obj):
        """
        Checks if a movie with the same title exists on the same show date.
        show_date_obj should be a python date or datetime object.
        """
        # ACF dates are usually stored/queried as YYYYMMDD or YYYY-MM-DD
        # Ensure this matches the 'Save Format' in your ACF settings
        date_str = show_date_obj.strftime("%Y%m%d")
        title_sanitised = su.sanitise_string(self.title)

        params = {
            "search": title,  # Broad search for the title
            "meta_key": "date",  # The name of your ACF field
            "meta_value": date_str,  # The value to match
            "status": "publish,future,draft",  # Check all statuses to avoid duplicates
        }

        response = requests.get(
            self.MOVIES_ENDPOINT,
            params=params,
            auth=HTTPBasicAuth(
                self.WORDPRESS_USERNAME,
                self.WORDPRESS_APPLICATION_KEY,
            ),
        )

        if response.status_code == 200:
            existing_movies = response.json()

            # The 'search' param is broad, so we verify exact matches
            for movie in existing_movies:
                # Check for exact title match (ignoring case)
                wp_title = movie.get("title", {}).get("rendered", "")
                wp_title = su.sanitise_string(wp_title)
                if title_sanitised in su.sanitise_string(wp_title):
                    # Double check the ACF date field specifically
                    # ACF data is often nested in the 'acf' key in REST response
                    acf_date = movie.get("acf", {}).get("date", "")
                    if acf_date == date_str:
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
            response = requests.get(self.MEDIA_ENDPOINT, auth=HTTPBasicAuth(self.WORDPRESS_USERNAME, self.WORDPRESS_APPLICATION_KEY), params=params)

            if response.status_code == 200:
                media_items = response.json()

                # Verify if the exact filename exists in the results
                for item in media_items:
                    source_url = item.get("source_url", "")
                    if file_name in source_url:
                        image_id = item.get("id")
                        # Return True and the actual ID
                        return True, image_id

                # No match found
                return False, None
            else:
                print(f"{Colour.RED}Failed to connect. Status code: {response.status_code}{Colour.RESET}")
                return False, None

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, None

    def upload_to_wordpress(self, path):
        credentials = f"{self.WORDPRESS_USERNAME}:{self.WORDPRESS_APPLICATION_KEY}"
        token = base64.b64encode(credentials.encode())
        headers = {
            "Authorization": f"Basic {token.decode('utf-8')}",
            "Content-Disposition": f"attachment; filename={os.path.basename(path)}",
            "Content-Type": "image/webp",
        }

        with open(path, "rb") as file:
            media_data = file.read()

        response = requests.post(self.MEDIA_ENDPOINT, headers=headers, data=media_data)

        if response.status_code == 201:
            # WordPress returns a dictionary of the new media object
            media_json = response.json()
            image_id = media_json.get("id")
            print(f"{Colour.GREEN}Image uploaded successfully. ID: {image_id}{Colour.RESET}")
            return image_id  # This is the vital piece
        else:
            print(f"{Colour.RED}Upload failed. Status code: {response.status_code}{Colour.RESET}")
            print(response.json())
            return None
