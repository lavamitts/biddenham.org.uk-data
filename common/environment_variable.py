from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from datetime import date


class EnvironmentVariable(object):
    def __init__(self, v, dtype="string", permit_omission=False):
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(env_path, override=True)

        v2 = os.getenv(v)
        if v2 is None:
            if permit_omission:
                self.value = ""
            else:
                print("Environment variable {v} not found.".format(v=v))
                sys.exit()
        else:
            if dtype in ("int", "num"):
                self.value = int(os.getenv(v).strip())
            elif dtype in ("bool", "boolean"):
                self.value = self.num_to_bool(os.getenv(v).strip())
            elif dtype in ("date", "datetime"):
                self.value = date.fromisoformat(os.getenv(v).strip())
            else:
                self.value = os.getenv(v).strip()

    def num_to_bool(self, num):
        num = num.strip().lower()
        if num == "true":
            return True
        elif num == "false":
            return False
        else:
            num = int(num)
            if num == 0:
                return False
            else:
                return True
