from enum import Enum


class Colour(Enum):
    """ANSI escape codes for terminal text formatting."""

    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def __str__(self):
        """Allows direct usage in f-strings."""
        return self.value
