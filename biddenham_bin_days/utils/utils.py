import os
import platform


def clear_console():
    # Determine the operating system
    current_os = platform.system()

    # Use the appropriate command based on the OS
    if current_os == "Windows":
        os.system("cls")
    else:
        os.system("clear")
