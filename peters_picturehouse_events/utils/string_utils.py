import re


def sanitise_string(s) -> str:
    if s is None:
        return ""

    # Convert to lowercase first
    s = s.strip().lower()

    # Standardise WordPress ampersand variations into the word 'and'
    s = s.replace("&#038;", " and ")
    s = s.replace("&amp;#038;", " and ")
    s = s.replace("&amp;", " and ")
    s = s.replace("&", " and ")

    # Remove smart apostrophes and standard apostrophes
    s = s.replace("&#8217;", "")
    s = s.replace("'", "")
    s = s.replace("’", "")

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
