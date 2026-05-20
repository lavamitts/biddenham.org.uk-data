from event_builder.classes.event_builder import EventBuilder
import utils.device_utils as du


def main():
    du.clear_console()
    event_builder = EventBuilder()
    event_builder.load_config()
    event_builder.choose_schedule()
    event_builder.generate_event_schedule()
    event_builder.generate_wordpress_events()


if __name__ == "__main__":
    main()
