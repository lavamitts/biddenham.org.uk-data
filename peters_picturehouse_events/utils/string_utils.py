import re


def sanitise_string(s) -> str:
    if s is None:
        return ""
    # Convert to lowercase first
    s = s.strip().lower()
    s = s.replace("&#8217;", "")
    s = s.replace("'", "")
    s = s.replace("’", "")
    # Replace apostrophes with hyphens or empty strings explicitly before managing spaces
    s = s.replace("'", "-").replace("’", "-")
    # Replace spaces with hyphens
    s = s.replace(" ", "-")
    # Remove any other rogue non-alphanumeric characters (except hyphens)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    # Collapse multiple consecutive hyphens into a single hyphen (e.g. king--s to king-s)
    return re.sub(r"-+", "-", s).strip("-")


def xsanitise_string(s) -> str:
    if s is None:
        return ""
    s = s.strip().lower()
    s = s.replace(" ", "-")
    return re.sub(r"[^a-z0-9\-]", "", s)


def YN(s):
    if s is None:
        return False
    else:
        s = str(s).strip().lower()
        if s in ["yes", "y"]:
            return True
        else:
            return False
