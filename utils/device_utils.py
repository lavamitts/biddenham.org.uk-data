import os
import sys
import platform


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


def clear_console():
    # Determine the operating system
    current_os = platform.system()

    # Use the appropriate command based on the OS
    if current_os == "Windows":
        os.system("cls")
    else:
        os.system("clear")
