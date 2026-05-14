import re


def sanitise_string(s) -> str:
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
