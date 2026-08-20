from common.style import Colour
from pathlib import Path
from requests.auth import HTTPBasicAuth
import base64
import os
import peters_picturehouse_events.config as config
import requests
import utils.file_utils as fu


class MovieImage(object):
    def __init__(self, title, title_sanitised):
        parent_path = os.path.join(os.getcwd(), "peters_picturehouse_events")
        self.image_dir = Path(parent_path, "resources/02. images")
        self.title = title
        self.title_sanitised = title_sanitised
        _ = 1

    def check_image_exists_in_wordpress(self):
        # Parameters to filter the search
        params = {"search": self.title_sanitised, "per_page": 10}

        try:
            response = requests.get(config.MEDIA_ENDPOINT, auth=HTTPBasicAuth(config.WORDPRESS_USERNAME, config.WORDPRESS_APPLICATION_KEY), params=params)

            if response.status_code == 200:
                media_items = response.json()

                # Verify if the exact filename exists in the results
                for item in media_items:
                    source_url = item.get("source_url", "")
                    if self.title_sanitised in source_url:
                        image_id = item.get("id")
                        # Return True and the actual ID
                        print("Image found in WordPress")
                        return True, image_id, source_url

                # No match found
                print("Image not found in WordPress")
                return False, None, None
            else:
                print(f"{Colour.RED}Failed to connect. Status code: {response.status_code}{Colour.RESET}")
                return False, None, None

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, None, None

    def find_and_upload_local_image(self):
        print(f"Image for {Colour.CYAN}{self.title}{Colour.RESET} not found in Wordpress media library. Searching locally ...")

        filename_to_find = f"{self.title_sanitised}.webp"
        success, filename = fu.find_file(config.IMAGES_FOLDER, filename_to_find)
        if success:
            self.upload_to_wordpress(filename)
            # self.month_added = du.get_month_number()
            # self.year_added = du.get_year()
            print(f"Uploading image for movie {Colour.GREEN}{self.title}{Colour.RESET} to Wordpress media library ...")
        else:
            print(f"\nImage file for movie {Colour.RED}{self.title}{Colour.RESET} not found. Please create an image for this movie before retrying.")
            return

    def upload_to_wordpress(self, path):
        credentials = f"{config.WORDPRESS_USERNAME}:{config.WORDPRESS_APPLICATION_KEY}"
        token = base64.b64encode(credentials.encode())
        headers = {
            "Authorization": f"Basic {token.decode('utf-8')}",
            "Content-Disposition": f"attachment; filename={os.path.basename(path)}",
            "Content-Type": "image/webp",
        }

        with open(path, "rb") as file:
            media_data = file.read()

        response = requests.post(config.MEDIA_ENDPOINT, headers=headers, data=media_data)

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
