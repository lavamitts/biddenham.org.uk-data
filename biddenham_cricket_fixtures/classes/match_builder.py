import csv
import os
import sys
from .match import Match
from .venue_collection import VenueCollection


class MatchBuilder(object):
    def __init__(self):
        self.resources_folder = os.path.join(os.getcwd(), "biddenham_cricket_fixtures", "resources")
        self.data_folder = os.path.join(self.resources_folder, "data")
        self.output_folder = os.path.join(self.resources_folder, "output")

        os.makedirs(self.output_folder, exist_ok=True)

        self.template_folder = os.path.join(self.resources_folder, "template")
        self.excel_source = os.path.join(self.data_folder, "picture-house-data.xlsx")
        self.current_template_file = os.path.join(self.template_folder, "current_template.txt")

        self.venue_collection = VenueCollection()
        self.venue_collection.load_venue_data()
        self.venue_collection.populate_wordpress_venues()

    def build_events(self):
        """Loops through all of the fixtures in the CSV master
        and creates entities for loading into WordPress for each.
        """

        # Pass 1 - Open the CSV file and read the fixtures
        # Check that all of the venues exist.
        filename = os.path.join(self.data_folder, "biddenham_fixtures.csv")
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            venues = []
            for row in csv_reader:
                match = Match(row, self.venue_collection)
                if not match.exclude:
                    venue = match.venue
                    if venue not in venues:
                        venues.append(venue)

        missing_venues = []
        for venue in venues:
            if venue not in self.venue_collection.venues_dict:
                missing_venues.append(venue)
                print(f"Error: Venue '{venue}' not found in venues collection.")

        if len(missing_venues) > 0:
            print("The following venues were missing from the venues collection:")
            for venue in missing_venues:
                print(f" - {venue}")
        _ = 1
        # sys.exit()

        # Pass 2 - Open the CSV file and read the fixtures
        # Create events in WordPress via the API for each fixture, as long as they aren't excluded by the check_for_exclusion method in the Match class.
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                match = Match(row, self.venue_collection)
                match.write_event()
