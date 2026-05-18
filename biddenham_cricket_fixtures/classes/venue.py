from common.environment_variable import EnvironmentVariable
import base64
import json
import sys
import peters_picturehouse_events.utils.string_utils as su
import urllib.parse
import urllib.request


class Venue(object):
    def __init__(self, row):
        self.data = row
        self.key: str = ""
        self.venue_name: str = ""
        self.address1: str = ""
        self.city: str = ""
        self.postcode: str = ""
        self.county: str = ""
        self.venue_id: int = None

        self.parse_data()

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

        # self.EVENTS_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"
        self.VENUE_ENDPOINT = f"{self.WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/venues"

    def parse_data(self):
        self.key = self.data.get("key", "")
        self.venue_name = self.data.get("venue_name", "")
        self.address1 = self.data.get("address1", "")
        self.city = self.data.get("city", "")
        self.postcode = self.data.get("postcode", "")
        self.county = self.data.get("county", "")
        self.venue_id = ""  # self.data.get("venue_id", "")
        _ = 1

    def check_venue_exists_in_wordpress(self):
        """
        Checks if a venue exists by its title using the WordPress REST API."""

        self.get_api_credentials()

        # URL-encode the search query to handle spaces and special characters
        query_params = urllib.parse.urlencode({"search": self.venue_name})
        url = f"{self.VENUE_ENDPOINT}?{query_params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Python-Client"})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())

                    # The API returns a list of matching posts. We check for an exact match.
                    for venue in data["venues"]:
                        # WordPress titles are often inside a nested dictionary: post['title']['rendered']
                        venue_name_to_match = su.sanitise_string(self.venue_name)
                        venue_name = su.sanitise_string(venue["venue"])
                        if venue_name == venue_name_to_match:
                            self.venue_id = venue["id"]
                            print(f"Match found: '{self.venue_name}' exists (ID: {venue.get('id')})")
                            _ = 1
                            return

                    print(f"No exact match found for '{self.venue_name}'.")
                    self.create_venue()
                    _ = 1
                    return None

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            sys.exit()
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            sys.exit()

        return None

    def create_venue(self):
        """Creates a new venue in The Events Calendar via the REST API."""
        # return
        # Map the input variables to the schema expected by The Events Calendar API
        payload = {
            "venue": self.venue_name,
            "address": self.address1,
            "city": self.city,
            "county": self.county,
            "zip": self.postcode,
            "country": "United Kingdom",
            "show_map": "True",
            "show_map_link": "True",
            "status": "publish",
        }

        # Encode the payload to JSON bytes
        json_data = json.dumps(payload).encode("utf-8")

        # Create the Basic Authentication header
        auth_string = f"{self.WORDPRESS_USERNAME}:{self.WORDPRESS_APPLICATION_KEY}"
        auth_encoded = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Type": "application/json",
            "User-Agent": "Python-Client",
        }

        # Set up the POST request
        req = urllib.request.Request(self.VENUE_ENDPOINT, data=json_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 201:  # 201 Created is the standard success code
                    result = json.loads(response.read().decode())
                    print(f"Success: Venue '{result.get('venue')}' created with ID {result.get('id')}.")
                    return result

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"HTTP Error {e.code}: {e.reason}")
            try:
                # Try to print the specific error message returned by WordPress
                wp_error = json.loads(error_body)
                print(f"WordPress Message: {wp_error.get('message')}")
            except json.JSONDecodeError:
                print(f"Response body: {error_body}")

        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")

        return None
