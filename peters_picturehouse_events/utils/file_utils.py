import os


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
