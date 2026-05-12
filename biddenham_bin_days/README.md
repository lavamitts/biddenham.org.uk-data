# Create bin data JSON file for use on Biddenham website (bin days)

This application:

- reads the source from an Excel spreadsheet, which is defined in the `.env` file in the `source_filename` variable, as per `env.sample`.

- it then generates a JSON file in the format required and saves it as `biddenham-bin-days.json` in the `resources/json` folder.

---

## Prerequisites

This project uses **uv** for dependency and Python version management. Ensure you have it installed before proceeding.

## Setup

You no longer need to manually manage virtual environments. The setup is now handled through a unified project synchronisation.

1.  **Sync the environment**
    Run the following command to create a lockfile and install all required dependencies (such as Pillow) into a managed environment:

    ```shell
    uv sync
    ```

    This should be carried out after a remote `dependabot` update.

2.  **Updating dependencies**
    If you need to add new packages, use the `add` command instead of editing requirements files manually:
    ```shell
    uv add requests
    ```
    
## Running

`uv run main.py`
