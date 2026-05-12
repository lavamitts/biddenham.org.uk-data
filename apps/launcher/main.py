import os
import sys

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


def run_biddenham_bin_days_data():
    print("\nCreating Biddenham bin days data...\n")

    from biddenham_bin_days.main import main

    main()


def validate_on_this_day_urls():
    print("\Validating OTD URLs...\n")

    from biddenham_on_this_day.main import main

    main()


def main():
    print("Select project to run:")
    print("1) Create Biddenham bin days data")
    print("2) OTD stuff")
    print("\nPress 1 or 2...")

    while True:
        choice = get_single_keypress()

        if choice == "1":
            run_biddenham_bin_days_data()
            break

        elif choice == "2":
            validate_on_this_day_urls()
            break


if __name__ == "__main__":
    main()
