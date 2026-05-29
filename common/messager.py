import re
import sys
from common.style import Colour


class Messager(object):
    def __init__(self, message: str, message_type: str, abend: bool = False):
        self.message = message
        self.message_type = message_type.lower().strip()

        # Regular expression to match ANSI escape codes
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        # Create a clean version of the message with no colour codes
        clean_message = ansi_escape.sub("", message)

        match self.message_type:
            case "error":
                print(f"\n{Colour.RED}ERROR{Colour.RESET}")
                print("=====")
                print(f"{message}\n")

            case "success":
                print(f"\n{Colour.GREEN}SUCCESS{Colour.RESET}")
                print("=======")
                print(f"{message}\n")

            case "complete":
                print(f"\n{Colour.GREEN}COMPLETE{Colour.RESET}")
                print("========")
                print(f"{message}\n")

            case "planned":
                print(f"\n{Colour.MAGENTA}END{Colour.RESET}")
                print("=====")
                print(f"{message}\n")

            case "level1" | "l1":
                # Use clean_message for the upper case text and the correct length
                underline = "=" * len(clean_message)
                print(f"\n\n{clean_message.upper()}")
                print(f"{Colour.CYAN}{underline}{Colour.RESET}\n")

            case "level2" | "l2":
                # Use clean_message for the upper case text and the correct length
                underline = "=" * len(clean_message)
                print(f"\n\n{clean_message.upper()}")
                print(f"{Colour.DIM}{underline}{Colour.RESET}")

            case "para" | "normal":
                print(f"{message}")

            case "indent" | "indented" | "bullet" | "bullets" | "bulleted":
                print(f"- {message}")

            case "dim":
                print(f"{Colour.DIM}{message}{Colour.RESET}")

        if abend:
            sys.exit()
