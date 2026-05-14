from common.environment_variable import EnvironmentVariable
from colorama import Fore, Style, init
from datetime import datetime
import json
import openpyxl
import os
from pathlib import Path
import biddenham_bin_days.utils.utils as u


class BinCalendarProcessor(object):
    def __init__(self):
        self.source_filename = EnvironmentVariable(
            "source_filename", "string", True
        ).value
        # print("Hello from BinCalendarProcessor!")
        # print(self.source_filename)
        # sys.exit(0)

    def process_calendar(self):
        u.clear_console()

        # Initialise colorama
        init(autoreset=True)

        # Load the Excel file
        workbook = openpyxl.load_workbook(self.source_filename, data_only=True)
        sheet = workbook.active

        data_dict = {}

        # Loop through rows, assuming first row is a header
        for row in sheet.iter_rows(min_row=2, values_only=True):
            date_cell = row[0]
            event_cell = row[1]

            if date_cell and event_cell:
                # Convert date to string (ISO format or your preferred format)
                if isinstance(date_cell, datetime):
                    date_str = date_cell.strftime("%Y-%m-%d")
                else:
                    date_str = str(date_cell)

                data_dict[date_str] = event_cell

        # Ensure folder exists
        BASE_DIR = Path(__file__).resolve().parents[1]
        output_path = BASE_DIR / "resources" / "json"
        os.makedirs(output_path, exist_ok=True)

        # Write to JSON file
        filename = "biddenham-bin-days.json"
        output_filename = os.path.join(output_path, filename)
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)

        print(f"\n{Fore.CYAN}COMPLETE{Style.RESET_ALL}\n========")
        print(
            f"\nData extracted to '{Fore.CYAN}{filename}{Style.RESET_ALL}' in the '{Fore.CYAN}resources/json{Style.RESET_ALL}' folder.\n"
        )
