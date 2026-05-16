import os
import platform
import sys


def clear_console():
    # Determine the operating system
    current_os = platform.system()

    # Use the appropriate command based on the OS
    if current_os == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# Windows-only single keypress support
if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios


def get_single_keypress() -> str:
    """
    Wait for a single keypress without requiring Enter.
    Supports Ctrl+C and Escape.
    """
    if os.name == "nt":
        key = msvcrt.getch()

        # Handle special keys (arrows, function keys, etc.)
        if key in (b"\x00", b"\xe0"):
            msvcrt.getch()
            return ""

        # Ctrl+C
        if key == b"\x03":
            raise KeyboardInterrupt

        return key.decode("utf-8", errors="ignore")

    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)

            # Ctrl+C
            if key == "\x03":
                raise KeyboardInterrupt

            return key

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def generate_peters_picturehouse_events():
    print("\nCreating Peter's Picturehouse events...\n")

    from peters_picturehouse_events.main import main

    main()


def run_biddenham_bin_days_data():
    print("\nCreating Biddenham bin days data...\n")

    from biddenham_bin_days.main import main

    main()


def generate_biddenham_conservation_volunteers_data():
    print("\nCreating Biddenham bin days data...\n")

    from biddenham_conservation_volunteers.main import main

    main()


def validate_on_this_day_urls():
    print("Validating OTD URLs...\n")

    from biddenham_on_this_day.main import main

    main()


def scrape_biddenham_cricket_fixtures():
    print("Scraping Biddenham Cricket Club fixtures...\n")

    from biddenham_cricket_fixtures.main import main

    main()


def main():
    clear_console()
    print("Select project to run:")
    print("1) Create Peter's Picturehouse events")
    print("2) Create Biddenham bin days data")
    print("3) Generate Biddenham Conservation Volunteers events")
    print("4) Validate On this day URLs")
    print("5) Scrape Biddenham Cricket Club fixtures")
    print("\nPress 1, 2, 3, 4 or 5 ...")

    while True:
        choice = get_single_keypress()

        if choice == "1":
            generate_peters_picturehouse_events()
            break

        elif choice == "2":
            run_biddenham_bin_days_data()
            break

        elif choice == "3":
            generate_biddenham_conservation_volunteers_data()
            break

        elif choice == "4":
            validate_on_this_day_urls()
            break

        elif choice == "5":
            scrape_biddenham_cricket_fixtures()
            break


if __name__ == "__main__":
    main()
