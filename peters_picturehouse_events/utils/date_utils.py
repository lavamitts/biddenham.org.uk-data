from datetime import datetime


def get_day_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    last_digit = day % 10
    if last_digit == 1:
        return 'st'
    elif last_digit == 2:
        return 'nd'
    elif last_digit == 3:
        return 'rd'
    else:
        return 'th'


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
