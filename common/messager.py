import sys
from common.style import Colour


class Messager(object):
    def __init__(self, message: str, message_type: str, abend: bool = False):
        self.message = message
        self.message_type = message_type

        match message_type:
            case "error":
                print(f"\n{Colour.RED}ERROR{Colour.RESET}")
                print("=====")
                print(f"{message}\n")

        if abend:
            sys.exit()
