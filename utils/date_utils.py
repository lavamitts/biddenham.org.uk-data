from datetime import datetime, date
import re
import sys


def get_day_suffix(day):
    if 11 <= day <= 13:
        return "th"
    last_digit = day % 10
    if last_digit == 1:
        return "st"
    elif last_digit == 2:
        return "nd"
    elif last_digit == 3:
        return "rd"
    else:
        return "th"


def is_before_today(input_date: datetime) -> bool:
    """
    Checks if the given datetime is before today (ignores time).

    Args:
        input_date (datetime): The datetime object to check.

    Returns:
        bool: True if the date is before today, False otherwise.
    """
    today = datetime.today().date()
    return input_date.date() < today


def get_month_number():
    return datetime.now().strftime("%m")


def get_year():
    return datetime.now().strftime("%Y")


def parse_custom_datetime(date_str: str, time_str: str, is_start: bool) -> datetime:
    """Converts custom date and time strings into a standard datetime object."""

    # Remove the day name (e.g., 'Wednesday ') from the start of the string
    # This avoids issues if the day name and day number do not match up
    date_clean = re.sub(r"^[A-Za-z]+\s+", "", date_str)

    # Remove the ordinal suffix (st, nd, rd, th) from the day number
    # For example, '20th May' becomes '20 May'
    date_clean = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_clean)

    # Add on the year on now
    year = date.today().year
    date_clean = f"{date_clean} {year}"

    # Combine the cleaned date string and the time string
    time_str = time_str.replace(".", ":")
    combined_str = f"{date_clean} {time_str}"

    # Parse the combined string
    # %d = Day of the month, %B = Full month name, %H.%M = Hour and minute separated by a dot

    try:
        ret = datetime.strptime(combined_str, "%d %B %Y %H:%M")
    except Exception as _:
        # print(f"Value: '{combined_str}' found in the date field that cannot be converted to a Python date.")
        ret = None
    return ret


def date_to_wordpress_date_string(date_obj):
    try:
        return date_obj.strftime("%Y-%m-%d %H:%M")
    except Exception as _:
        return None


def date_to_simple_date_string(date_obj):
    try:
        return date_obj.strftime("%Y-%m-%d")
    except Exception as _:
        return None


def iso_date_string_to_date(s: str) -> date:
    try:
        date_obj = datetime.strptime(s, "%Y-%m-%d").date()
    except Exception as e:
        print(e)
        sys.exit()
    return date_obj


def get_date_time_pair(s: str):
    # "2026-03-10 19:30 - 21:30"
    parts = s.split(" ", 1)
    date_string = parts[0]
    date_obj = iso_date_string_to_date(date_string)
    times = parts[1]
    start, end = [x.strip() for x in times.split("-")]

    start_dt = datetime.combine(date_obj, datetime.strptime(start, "%H:%M").time())
    end_dt = datetime.combine(date_obj, datetime.strptime(end, "%H:%M").time())
    return start_dt, end_dt
    _ = 1


def convert_string_to_date(date_string: str, date_format: str = "%Y-%m-%d") -> date:
    """Converts a date string into a date object."""
    return datetime.strptime(date_string, date_format).date()


# def get_day_suffix(day: int) -> str:
#     """Returns the appropriate ordinal suffix for a given day of the month."""
#     if 11 <= day <= 13:
#         return "th"
#     return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def convert_date_to_custom_string(date_object: date) -> str:
    """Converts a date object into a string formatted as 'Weekday, Day Month Year'."""
    day = date_object.day
    suffix = get_day_suffix(day)

    # %A = Weekday, %B = Full Month Name, %Y = 4-digit Year
    day_str = f"{day}{suffix}"
    return date_object.strftime(f"%A, {day_str} %B %Y")


def get_current_year_and_month():
    """Returns the current year and month as two-digit strings."""
    now = datetime.now()

    year_str = now.strftime("%Y")  # e.g., "26" for 2026
    month_str = now.strftime("%m")  # e.g., "05" for May

    return year_str, month_str
