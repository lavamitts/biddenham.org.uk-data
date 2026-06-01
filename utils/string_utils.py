import re
from common.style import Colour


def standardise_whitespace(s):
    # Replace all whitespace sequences with a single space
    if s is None:
        return ""
    s = re.sub(r"\s+", " ", s)
    return s


def print_heading(s):
    s = s.strip()
    print(s.upper())
    underline = "=" * len(s)
    print(f"{Colour.BRIGHT_CYAN}{underline}{Colour.RESET}")


def list_to_sentence(items) -> str:
    if not items:
        result = ""
    elif len(items) == 1:
        result = items[0]
    else:
        result = ", ".join(items[:-1]) + " and " + items[-1]

    return result


def sanitise_string(s) -> str:
    if s is None:
        return ""

    # Convert to lowercase first
    s = s.strip().lower()

    # Remove smart apostrophes and standard apostrophes
    s = s.replace("&#8217;", "")
    s = s.replace("'", "")
    s = s.replace("’", "")

    # Hyphens
    s = s.replace("&#8211;", "-")

    # Standardise WordPress ampersand variations into the word 'and'
    s = s.replace("&#038;", " and ")
    s = s.replace("&amp;#038;", " and ")
    s = s.replace("&amp;", " and ")
    s = s.replace("&", " and ")

    # Replace spaces (and new spaces created by the ampersand replacement) with hyphens
    s = s.replace(" ", "-")

    # Remove any other rogue non-alphanumeric characters (except hyphens)
    s = re.sub(r"[^a-z0-9\-]", "", s)

    # Collapse multiple consecutive hyphens into a single hyphen
    return re.sub(r"-+", "-", s).strip("-")


def YN(s):
    if s is None:
        return False
    else:
        s = str(s).strip().lower()
        if s in ["yes", "y"]:
            return True
        else:
            return False


def add_file_extension(s: str, extension: str = "docx"):
    if s is None:
        return ""
    else:
        s = s.strip()
        if "." not in s:
            s = f"{s}.{extension}"
        return s


def format_runtime(runtime_str: str) -> str:
    # Extract the minute number
    minutes = int(runtime_str.replace(" min", "").strip())

    hrs = minutes // 60
    mins = minutes % 60

    parts = []

    if hrs > 0:
        parts.append(f"{hrs} hr" if hrs == 1 else f"{hrs} hrs")

    if mins > 0:
        parts.append(f"{mins} min" if mins == 1 else f"{mins} mins")

    # return {"Runtime": " ".join(parts)}
    return " ".join(parts)


def get_date_folders_from_url(url):
    # Remove any trailing slashes to prevent empty elements at the end
    cleaned_url = url.rstrip("/")

    # Split the URL by forward slashes
    parts = cleaned_url.split("/")

    # Check that the URL has enough segments to avoid an IndexError
    if len(parts) >= 3:
        # -2 gets the second to last item, -3 gets the third to last item
        second_last = parts[-2]
        third_last = parts[-3]
        return third_last, second_last

    return None, None
