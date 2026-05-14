import os
from datetime import date
import peters_picturehouse_events.utils.date_utils as du
import peters_picturehouse_events.utils.string_utils as su


class Movie(object):
    def __init__(self, row):
        self.resources_folder = os.path.join(
            os.getcwd(), "peters_picturehouse_events", "resources"
        )
        self.template_folder = os.path.join(self.resources_folder, "template")
        self.output_folder = os.path.join(self.resources_folder, "output")
        self.event_folder = os.path.join(self.output_folder, "event")
        self.listing_folder_old = os.path.join(self.output_folder, "listing-old")
        self.listing_folder = os.path.join(self.output_folder, "listing")

        # Make folders if they don't exist
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.event_folder, exist_ok=True)
        os.makedirs(self.listing_folder_old, exist_ok=True)
        os.makedirs(self.listing_folder, exist_ok=True)

        self.data = row
        self.process_data()
        self.get_date_string()
        self.generate_html()

    def process_data(self):
        self.show_date: date = self.data[0]
        self.show_year: str = str(self.show_date.year)
        self.title: str = self.data[1]
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

    def is_valid(self):
        return self.title is not None and self.title != ""

    def get_date_string(self):
        if not self.is_valid():
            return
        dt = self.show_date
        day = dt.day
        suffix = du.get_day_suffix(day)
        self.date_formatted = dt.strftime(f"%A, {day}{suffix} %B %Y")

    def generate_html(self):
        if not self.is_valid():
            return
        self.filename = f"{su.sanitise_string(self.title)}.html"
        self.filename_as_text = f"{su.sanitise_string(self.title)}.html.txt"
        self.generate_event()
        self.generate_listing()

    def generate_event(self):
        event_template: str = os.path.join(self.template_folder, "event_template.txt")
        os.makedirs(self.event_folder, exist_ok=True)
        os.makedirs(os.path.join(self.event_folder, self.show_year), exist_ok=True)
        event_filename: str = os.path.join(
            self.event_folder, self.show_year, self.filename
        )

        # event_filename = os.path.join(self.event_folder, self.filename)
        # Open the template
        with open(event_template, "r", encoding="utf-8") as file:
            template_content = file.read()

        # Make replacements
        self.event_content = self.replace_placeholders(template_content)

        # Save the resultant file
        with open(event_filename, "w", encoding="utf-8") as file:
            file.write(self.event_content)

    def generate_listing(self):
        # Get the HTML templates
        # It's crucial that this remains with a .txt extension, as opening with a .html extension causes issues
        # probably due to Prettier changing small details of the file imperceptbly.
        html_listing_template: str = os.path.join(
            self.template_folder, "listing_template.html.txt"
        )

        # Make the subfolders
        os.makedirs(
            os.path.join(self.listing_folder_old, self.show_year), exist_ok=True
        )
        os.makedirs(os.path.join(self.listing_folder, self.show_year), exist_ok=True)

        # Get the filename for the new listing
        listing_filename: str = os.path.join(
            self.listing_folder, self.show_year, self.filename_as_text
        )

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
            s = s.replace("{title_formatted}", self.filename.replace(".html", ""))
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
