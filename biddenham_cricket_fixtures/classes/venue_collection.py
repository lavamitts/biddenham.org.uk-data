import csv
import os
import sys
from .venue import Venue


class VenueCollection(object):
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), "biddenham_cricket_fixtures", "resources", "data", "venues.csv")
        _ = 1

    def load_venue_data(self):
        self.venues_dict = {}

        try:
            with open(self.file_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Clean up any accidental leading or trailing whitespace
                    cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                    venue = Venue(cleaned_row)
                    self.venues_dict[venue.key] = venue

            _ = 1

        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' could not be found.")
            sys.exit(1)

    def populate_wordpress_venues(self):
        for venue_key, venue in self.venues_dict.items():
            venue.check_venue_exists_in_wordpress()
            _ = 1
