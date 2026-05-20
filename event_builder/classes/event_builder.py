from datetime import date, timedelta
import json
import os
from event_builder.classes.event import Event
import utils.date_utils as du
from common.messager import Messager


WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class EventBuilder(object):
    def __init__(self):
        self.resources_folder = os.path.join(os.getcwd(), "event_builder", "resources")
        self.config_folder = os.path.join(self.resources_folder, "config")
        self.config_file = os.path.join(self.config_folder, "event_builder_config.json")

    def load_config(self):
        self.config_data = {}
        with open(self.config_file, "r") as file:
            self.config_data = json.load(file)

    def choose_schedule(self):
        """
        Ask user which schedule they want to run.
        """

        self.selected_schedule = None
        self.selected_config = None
        schedules = list(self.config_data["data"].keys())

        print("\nAvailable schedules:\n")

        for index, schedule_name in enumerate(schedules, start=1):
            print(f"{index}. {schedule_name}")

        while True:
            try:
                choice = int(input("\nChoose a schedule number: "))

                if 1 <= choice <= len(schedules):
                    self.selected_schedule = schedules[choice - 1]
                    break

                print("Invalid choice. Try again.")

            except ValueError:
                print("Please enter a valid number.")

        if self.selected_schedule:
            self.selected_config = self.config_data["data"][self.selected_schedule]

    def generate_event_schedule(self):
        """
        Generates schedule for a single event.

        event_name=selected_schedule,
        config=selected_config,

        """

        self.events = []

        # Either all of these, or specific dates must have been completed
        # If both are completed, then we should error ourt for clarity
        day_of_week = self.selected_config.get("day_of_week", None)
        week_of_month = self.selected_config.get("week_of_month", None)
        start_year = self.selected_config.get("start_year", None)
        end_year = self.selected_config.get("end_year", None)

        # Count up the parameters
        schedule_route_parameter_count = sum(
            bool(v)
            for v in (
                day_of_week,
                week_of_month,
                start_year,
                end_year,
            )
        )

        # Variables used to bound the creation within a start and end date, but still according to the set schedule
        earliest_date_string = self.selected_config.get("earliest_date", None)
        latest_date_string = self.selected_config.get("latest_date", None)

        # Alternative route is specific dates
        specific_date_times = self.selected_config.get("specific_date_times", [])

        if len(specific_date_times) != 0:
            if schedule_route_parameter_count > 0:
                Messager(
                    "Please specify only a schedule or specific dates, not both.",
                    "error",
                    True,
                )
        elif schedule_route_parameter_count != 4:
            Messager(
                "Please ensure that all schedule-related fields are supplied.",
                "error",
                True,
            )

        if specific_date_times:
            # Specific dates and time have been supplied
            for specific_date_time in specific_date_times:
                date_time_pair = du.get_date_time_pair(specific_date_time)
                _ = 1
                event = Event("specific", date_time_pair, None, None, self.selected_config)
                self.events.append(event)
            _ = 1
        else:
            # We are following a monthly schedule
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    event_date = self.get_nth_weekday(
                        year=year,
                        month=month,
                        weekday_name=day_of_week,
                        week_of_month=week_of_month,
                    )

                    process_event = True
                    # Compare event date against optional event boundaries
                    if earliest_date_string is not None:
                        earliest_date = du.iso_date_string_to_date(earliest_date_string)
                        if event_date < earliest_date:
                            process_event = False
                    if latest_date_string is not None:
                        latest_date = du.iso_date_string_to_date(latest_date_string)
                        if event_date > latest_date:
                            process_event = False

                    if process_event:
                        event = Event(
                            "schedule",
                            event_date,
                            month,
                            year,
                            self.selected_config,
                        )
                        self.events.append(event)

    def get_nth_weekday(self, year, month, weekday_name, week_of_month):
        """
        Returns the nth weekday in a given month.
        """

        target_weekday = WEEKDAY_MAP[weekday_name.lower()]

        current = date(year, month, 1)

        # Find first matching weekday
        while current.weekday() != target_weekday:
            current += timedelta(days=1)

        # Move to nth occurrence
        current += timedelta(weeks=week_of_month - 1)

        return current

    def generate_wordpress_events(self):
        _ = 1
        for event in self.events:
            event.generate_wordpress_event()
