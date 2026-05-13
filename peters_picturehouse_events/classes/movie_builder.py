import csv
import openpyxl  # type: ignore
import os
from .movie import Movie
from .event import Event
import peters_picturehouse_events.utils.date_utils as du


class MovieBuilder(object):
    def __init__(self):
        self.resources_folder = os.path.join(
            os.getcwd(), "peters_picturehouse_events", "resources"
        )
        self.input_folder = os.path.join(self.resources_folder, "input")
        self.output_folder = os.path.join(self.resources_folder, "output")

        os.makedirs(self.output_folder, exist_ok=True)

        self.template_folder = os.path.join(self.resources_folder, "template")
        self.excel_source = os.path.join(self.input_folder, "picture-house-data.xlsx")
        self.current_template_file = os.path.join(
            self.template_folder, "current_template.txt"
        )
        self.archive_template_file = os.path.join(
            self.template_folder, "archive_template.txt"
        )
        self.archive_intro_file = os.path.join(
            self.template_folder, "archive_intro.txt"
        )
        self.event_scv_file = os.path.join(self.output_folder, "events.csv")

        self.get_archive_templates()

    def get_archive_templates(self):
        # Get template file for current schedule
        with open(self.current_template_file, "r", encoding="utf-8") as file:
            self.current_template = file.read()

        # Get template file for each year
        with open(self.archive_template_file, "r", encoding="utf-8") as file:
            self.archive_template = file.read()

        # Get intro bumph
        with open(self.archive_intro_file, "r", encoding="utf-8") as file:
            self.archive_intro = file.read()

    def build(self):
        self.movies = []
        # Load the Excel workbook
        workbook = openpyxl.load_workbook(self.excel_source)
        sheet = workbook["movies"]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            movie = Movie(row)
            if movie.is_valid():
                self.movies.append(movie)

    def compile_archive(self):
        years = {}
        for movie in self.movies:
            if du.is_before_today(movie.show_date):
                year = str(movie.show_date.year)
                if year not in years:
                    years[year] = []
                years[year].append(movie)

        # Sort the list of movies ... most recent 1st
        for year, movie_list in years.items():
            years[year] = sorted(
                movie_list, key=lambda movie: movie.show_date, reverse=True
            )

        # Sort the list of years ... most recent 1st
        sorted_years = dict(
            sorted(years.items(), key=lambda x: int(x[0]), reverse=True)
        )

        # Compile each year's content
        self.archive_content = self.archive_intro + "\n"
        for year in sorted_years:
            # print(year)
            year_content = self.archive_template.replace("{year}", year)
            movie_list = ""
            for movie in sorted_years[year]:
                movie_list += movie.listing_html + "\n"

            year_content = year_content.replace("{content}", movie_list)
            self.archive_content += year_content

        # Write the data
        archive_filename = os.path.join(self.output_folder, "archive.html")
        with open(archive_filename, "w", encoding="utf-8") as file:
            file.write(self.archive_content)

    def compile_current(self):
        years = {}
        for movie in self.movies:
            if not du.is_before_today(movie.show_date):
                year = str(movie.show_date.year)
                if year not in years:
                    years[year] = []
                years[year].append(movie)

        # Sort the list of movies ... most recent 1st
        for year, movie_list in years.items():
            years[year] = sorted(
                movie_list, key=lambda movie: movie.show_date, reverse=False
            )

        # Sort the list of years ... most recent 1st
        sorted_years = dict(
            sorted(years.items(), key=lambda x: int(x[0]), reverse=False)
        )

        # Compile each year's content
        content = ""
        for year in sorted_years:
            movie_list = ""
            for movie in sorted_years[year]:
                movie_list += movie.listing_html + "\n"

            content += movie_list

        # Insert into the template
        content = self.current_template.replace("{content}", content)

        # Write the data
        current_filename = os.path.join(self.output_folder, "current.html")
        with open(current_filename, "w", encoding="utf-8") as file:
            file.write(content)

    def xbuild_events_csv(self):
        self.events = []
        for movie in self.movies:
            if not movie.imported:
                event = Event(movie)
                self.events.append(event)
                # print(f"Building CSV entry for {movie.title}")

    def build_events_csv(self):
        # Open a file to write CSV data
        with open(
            self.event_scv_file, mode="w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

            # Write header row (optional but recommended)
            writer.writerow(
                [
                    "Name",
                    "Description",
                    "Date From",
                    "Date To",
                    "Time From",
                    "Time To",
                    "Venue",
                    "Organiser",
                    "Currency Symbol",
                    "ISO Currency Code",
                    "Cost",
                    "Show map",
                    "Show map link",
                    "Event categories",
                ]
            )

            imported_count = 0
            for movie in self.movies:
                if imported_count > 0:
                    break

                if not movie.imported:
                    # print(f"Building CSV entry for {movie.title}")
                    event = Event(movie)
                    event.populate_event()
                    # self.events.append(event)
                    writer.writerow(event.to_csv_row())
                    imported_count += 1
