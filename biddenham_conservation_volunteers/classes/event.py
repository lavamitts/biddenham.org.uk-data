import os


class Event(object):
    def __init__(self, row, venue_collection):
        self.resources_folder = os.path.join(os.getcwd(), "biddenham_cricket_fixtures", "resources")
