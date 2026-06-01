from common.environment_variable import EnvironmentVariable
import os


# Load the base environment variables once
WORDPRESS_USERNAME = EnvironmentVariable("WORDPRESS_USERNAME", "string", False).value
WORDPRESS_APPLICATION_KEY = EnvironmentVariable("WORDPRESS_APPLICATION_KEY", "string", False).value
PETERS_PICTUREHOUSE_EARLIEST_DATE = EnvironmentVariable("PETERS_PICTUREHOUSE_EARLIEST_DATE", "date", False).value
WORDPRESS_SITE_URL = EnvironmentVariable("WORDPRESS_SITE_URL", "string", False).value
MOVIE_IMAGE_FOLDER = EnvironmentVariable("MOVIE_IMAGE_FOLDER", "string", False).value

# Construct the endpoints based on the site URL
EVENTS_ENDPOINT = f"{WORDPRESS_SITE_URL}/wp-json/tribe/events/v1/events"
MEDIA_ENDPOINT = f"{WORDPRESS_SITE_URL}/wp-json/wp/v2/media"
MOVIES_ENDPOINT = f"{WORDPRESS_SITE_URL}/wp-json/wp/v2/movies"

# Folders
RESOURCES_FOLDER = os.path.join(os.getcwd(), "peters_picturehouse_events", "resources")
TEMPLATE_FOLDER = os.path.join(RESOURCES_FOLDER, "template")
OUTPUT_FOLDER = os.path.join(RESOURCES_FOLDER, "output")
OUTPUT_LISTING_FOLDER = os.path.join(OUTPUT_FOLDER, "listing")

INPUT_FOLDER = os.path.join(RESOURCES_FOLDER, "00. input")
CONFIG_FOLDER = os.path.join(RESOURCES_FOLDER, "01. config")
OMDB_FOLDER = os.path.join(RESOURCES_FOLDER, "02. omdb")
IMAGES_FOLDER = os.path.join(RESOURCES_FOLDER, "03. images")
SUMMARY_FOLDER = os.path.join(RESOURCES_FOLDER, "04. summary")
DEBUG_FOLDER = os.path.join(RESOURCES_FOLDER, "05. debug")
LISTING_FOLDER = os.path.join(RESOURCES_FOLDER, "06. listing")
