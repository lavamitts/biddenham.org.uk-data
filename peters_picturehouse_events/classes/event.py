import csv
from io import StringIO


class Event(object):
    def __init__(self, movie):
        self.movie = movie

    def populate_event(self):
        self.name = self.movie.title
        self.description = self.movie.event_content
        self.date_from = self.movie.show_date
        self.date_to = self.movie.show_date
        self.time_from = "19:00"
        self.time_to = "21:30"
        self.venue = "Village Hall"
        self.organiser = "Peter's Picturehouse"
        self.currency_symbol = "£"
        self.iso_currency_code = "GBP"
        self.cost = "5.00"
        self.show_map = True
        self.show_map_link = True
        self.event_categories = "Peter's Picturehouse"

    def to_csv_row(self):
        # Return a list representing the CSV row
        return [
            self.name,
            self.description,
            self.date_from,
            self.date_to,
            self.time_from,
            self.time_to,
            self.venue,
            self.organiser,
            self.currency_symbol,
            self.iso_currency_code,
            self.cost,
            self.show_map,
            self.show_map_link,
            self.event_categories,
        ]

    def to_csv_string(self):
        # Use StringIO to create a CSV-formatted string safely
        output = StringIO()
        quote_requirement = csv.QUOTE_MINIMAL
        quote_requirement = csv.QUOTE_ALL
        writer = csv.writer(output, quoting=quote_requirement)
        writer.writerow(self.to_csv_row())
        return output.getvalue().strip()  # Remove trailing newline
