import curses
import json
import os
# from common.messager import Messager


def select_docx_file(folder_path, extension: str = None):
    # Get all .docx (etc.) files in the directory
    if extension is not None:
        extension = extension.replace(".", "")
    try:
        if extension:
            files = [f for f in os.listdir(folder_path) if f.endswith(f".{extension}") and os.path.isfile(os.path.join(folder_path, f))]
        else:
            files = [f for f in os.listdir(folder_path) if f != ".DS_Store" and os.path.isfile(os.path.join(folder_path, f))]

        if files:
            files = sorted([f for f in os.listdir(folder_path) if f.endswith(f".{extension}") and "$" not in f and os.path.isfile(os.path.join(folder_path, f))], reverse=True)

    except Exception as e:
        print(f"Error accessing folder: {e}")
        return None

    if not files:
        print("No matching files found in the specified folder.")
        return None

    def menu(stdscr):
        # Hide the blinking text cursor
        curses.curs_set(0)

        # Initialize color support and use the terminal's default background
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

        # Keep track of which file is currently highlighted
        current_row = 0

        while True:
            stdscr.clear()

            # Display instructions
            stdscr.addstr(0, 0, "Use Up  Down arrows to navigate, Enter to select, Escape to exit.", curses.A_REVERSE)
            stdscr.addstr(1, 0, f"Folder: {folder_path}\n")

            # Draw the list of files
            for idx, filename in enumerate(files):
                # Highlight the currently selected row
                if idx == current_row:
                    stdscr.attron(curses.A_STANDOUT)
                    stdscr.addstr(idx + 3, 2, filename)
                    stdscr.attroff(curses.A_STANDOUT)
                else:
                    stdscr.addstr(idx + 3, 2, filename)

            stdscr.refresh()

            # Wait for user input
            key = stdscr.getch()

            # Handle navigation and selection
            if key == curses.KEY_UP:
                current_row = (current_row - 1) % len(files)
            elif key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(files)
            elif key in [curses.KEY_ENTER, 10, 13]:  # Enter keys
                return files[current_row]
            elif key == 27:  # Escape key
                return None

    # Run the curses application safely
    return curses.wrapper(menu)


def find_file(root_folder, target_filename):
    # Ensure the path is expanded if using tilde or relative paths
    root_folder = os.path.expanduser(root_folder)

    # Check if the directory actually exists
    if not os.path.exists(root_folder):
        return f"Error: The path {root_folder} does not exist."

    # Walk through the directory tree
    for root, dirs, files in os.walk(root_folder):
        if target_filename in files:
            # Join the current directory path with the filename
            return (
                True,
                os.path.join(root, target_filename),
            )

    return (
        False,
        "File not found.",
    )


def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """Reads the entire content of a file and returns it as a string."""
    with open(file_path, "r", encoding=encoding) as file:
        return file.read()


def load_json_if_exists(filepath):
    """
    Check if a file exists and return JSON content if it does.
    Returns None if the file doesn't exist.
    """

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    return None
