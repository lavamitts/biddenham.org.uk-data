import utils.device_utils as deu
import utils.string_utils as su
from common.style import Colour


def generate_peters_picturehouse_events():
    su.print_heading("\nCreating Peter's Picturehouse events\n")
    from peters_picturehouse_events.main import main

    main()


def run_biddenham_bin_days_data():
    su.print_heading("\nCreating Peter's Picturehouse events\n")

    from biddenham_bin_days.main import main

    main()


def generate_biddenham_conservation_volunteers_data():
    su.print_heading("\nCreating events for Biddenham Conservation volunteers\n")

    from biddenham_conservation_volunteers.main import main

    main()


def validate_on_this_day_urls():
    su.print_heading("\nValidating OTD URLs...\n")

    from biddenham_on_this_day.main import main

    main()


def make_cricket_badges():
    su.print_heading("\Making Biddenham Cricket Club badges\n")

    from cricket_badges.main import main

    main()


def build_regular_events():
    su.print_heading("\Making Events\n")

    from event_builder.main import main

    main()


def scrape_fringe_data():
    su.print_heading("\Scraping fringe data\n")

    from fringe.main import process_fringe_data

    process_fringe_data()


def main():
    deu.clear_console()

    # Define the menu structure using function objects as values
    menu_options = {
        "1": {"text": "Create Peter's Picturehouse events", "func": generate_peters_picturehouse_events},
        "2": {"text": "Create Biddenham bin days data", "func": run_biddenham_bin_days_data},
        "3": {"text": "Create Biddenham Conservation Volunteers events", "func": generate_biddenham_conservation_volunteers_data},
        "4": {"text": "Validate On this day URLs", "func": validate_on_this_day_urls},
        "5": {"text": "Make cricket badges", "func": make_cricket_badges},
        "6": {"text": "Build regular events", "func": build_regular_events},
        "7": {"text": "Scrape fringe data", "func": scrape_fringe_data},
    }

    # Print the menu dynamically from the dictionary
    print(f"\n\n{Colour.BRIGHT_YELLOW}Select project to run{Colour.RESET}:\n")
    for key, option in menu_options.items():
        print(f"{Colour.BRIGHT_CYAN}{key}){Colour.RESET} {option['text']}")

    # Dynamically generate the footer message based on the keys
    valid_keys = ", ".join(menu_options.keys())
    print(f"\nPress {valid_keys} ...")

    while True:
        choice = deu.get_single_keypress()

        # Check if the keystroke matches a valid menu key
        if choice in menu_options:
            deu.clear_console()
            # Retrieve the function object and execute it by adding brackets ()
            menu_options[choice]["func"]()
            break


if __name__ == "__main__":
    main()
