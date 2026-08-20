import inquirer
from datetime import date
from common.messager import Messager
from common.style import Colour


class MovieDataCapture(object):
    def __init__(self):
        self.event_date = ""
        self.movie_title = ""
        self.movie_release_year = ""

    def get_event_date(self):
        """Prompts the user for the event year, month, and day sequentially,

        returning a string formatted as yyyy-dd-mm.
        """
        current_year = date.today().year
        current_month_index = date.today().month - 1  # 0-indexed for the months list
        next_year = current_year + 1

        Messager("Please enter the date on which the movie will be shown", "level1")

        # 1. Select the year
        # print("Select the year:\n")
        year_question = [
            inquirer.List(
                "year",
                message="Select the year in which the movie will be shown",
                choices=[str(current_year), str(next_year)],
            )
        ]
        year_answers = inquirer.prompt(year_question)
        selected_year = int(year_answers["year"])

        # 2. Select the month
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        # Determine the default month name based on the current date
        default_month = months[current_month_index]

        month_question = [
            inquirer.List(
                "month",
                message=f"Select the month in {Colour.CYAN}{selected_year}{Colour.RESET} which the movie will be shown",
                choices=months,
                default=default_month,  # Sets the default to the current month
            )
        ]
        month_answers = inquirer.prompt(month_question)
        # Convert month name to its corresponding integer (1-12)
        selected_month = months.index(month_answers["month"]) + 1
        selected_month_name = months[selected_month - 1]

        # 3. Calculate the default day (First Tuesday of the selected month)
        # Start at the 1st of the month
        first_of_month = date(selected_year, selected_month, 1)
        # weekday() returns 0 for Monday, 1 for Tuesday, etc.
        days_until_tuesday = (1 - first_of_month.weekday() + 7) % 7
        first_tuesday = 1 + days_until_tuesday

        # 4. Input the day with the pre-populated default
        while True:
            day_question = [
                inquirer.Text(
                    "day",
                    message=f"On which day in {Colour.CYAN}{selected_month_name}{Colour.RESET} will the movie be shown ({Colour.DIM}1st Tuesday by default{Colour.RESET})",
                    default=str(first_tuesday),
                )
            ]
            day_answers = inquirer.prompt(day_question)
            day_input = day_answers["day"].strip()

            try:
                # Validate if the entered day forms a genuine calendar date
                valid_date = date(selected_year, selected_month, int(day_input))

                # Format the final string specifically as yyyy-dd-mm
                # %Y = Year, %d = Zero-padded day, %m = Zero-padded month
                self.event_date = valid_date.strftime("%Y-%m-%d")
                return

            except ValueError:
                print("Invalid day for the selected month and year. Please try again.")

    def get_movie_title(self):
        """Prompts the user for a movie name and ensures it is not empty."""
        Messager("Movie name", "level2")
        while True:
            # Prompt the user for input and remove any leading or trailing whitespace

            movie_name = input(f"Enter the movie name {Colour.DIM}(as accurately as possible){Colour.RESET}: ").strip()

            # Check if the string is not empty after stripping whitespace
            if movie_name:
                self.movie_title = movie_name
                return

            # Feedback for the user if they pressed enter without typing anything
            print("Input cannot be empty. Please enter a valid movie name.")

    def get_movie_year(self):
        """Prompts the user for a movie release year."""

        Messager("Year of release", "level2")
        Messager("This parameter is optional. Only enter the year of release if there might be more than one.\n", "dim")
        self.movie_release_year = input("Optionally enter the year the movie was released:").strip()
