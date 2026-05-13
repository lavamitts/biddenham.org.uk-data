# Management of Biddenham Conservation Volunteers data for Biddenham Village

![Biddenham Conservation Volunteers logo](resources/assets/conservation-volunteers-logo-2webp)

## Installation

- Create a virtual environment and activate it:

  ```shell
  uv venv .venv
  source .venv/bin/activate  # (MacOS)
  .venv\Scripts\Activate  # (Windows)
  ```

- Install the required packages:

  ```shell
  uv pip install -r requirements.txt
  ```

## Running

`python create_events.py`

This will take the Word file that is specified in the script and generate individual pieces of HTML with the filename format `task{nn}.txt`, each of which contains the HTML needed to ppulate the respective events in the biddenham.org.uk event calendar.

Save Word documents in the format provided in the folder `resources/input`.

Copy the table wholesale into the [Biddenham Conservation Volunteers page](https://biddenham.org.uk/wp-admin/post.php?post=6050&action=edit) on the biddenham.org.uk website, then:



- set the table to be not fixed width.
- apply the CSS class `conservation-volunteers` to the table.