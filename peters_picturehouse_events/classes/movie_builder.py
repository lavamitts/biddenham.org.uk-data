import openpyxl
import os
from .movie import Movie


class MovieBuilder(object):
    def __init__(self):
        self.resources_folder = os.path.join(os.getcwd(), "peters_picturehouse_events", "resources")
        self.input_folder = os.path.join(self.resources_folder, "input")
        self.output_folder = os.path.join(self.resources_folder, "output")

        os.makedirs(self.output_folder, exist_ok=True)

        self.template_folder = os.path.join(self.resources_folder, "template")
        self.excel_source = os.path.join(self.input_folder, "picture-house-data.xlsx")
        self.current_template_file = os.path.join(self.template_folder, "current_template.txt")

    def build(self):
        """Loops through all of the movies in the Excel master sheet
        and creates entities for loading into WordPress for each.
        """
        self.movies = []
        # Load the Excel workbook
        workbook = openpyxl.load_workbook(self.excel_source)
        sheet = workbook["movies"]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            movie = Movie(row)
            if movie.is_valid_movie():
                self.movies.append(movie)
