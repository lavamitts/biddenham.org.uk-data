import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_web_data(url):
    """Fetches the status code and HTML title for a given URL."""
    try:
        # Using a timeout to prevent the script from hanging on broken links
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        status = response.status_code

        if status == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.title.string.strip() if soup.title else "No title found"
        else:
            title = "N/A"

        return status, title
    except Exception as e:
        return "Error", str(e)


def process_folder(folder_path):
    results = []

    # Filter for only .json files in the directory
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Handle both a single object or a list of objects per file
                if isinstance(data, dict):
                    data = [data]

                for record in data:
                    record_date = record.get("date", "Unknown")
                    events = record.get("events", [])

                    for event in events:
                        title = event.get("title")
                        url = event.get("url")

                        if url:
                            print(f"Checking: {url}")
                            status, page_title = get_web_data(url)

                            results.append(
                                {
                                    "JSON Filename": filename,
                                    "Record Date": record_date,
                                    "Event Title": title,
                                    "URL": url,
                                    "HTTP Status": status,
                                    "Page Title": page_title,
                                }
                            )
            except json.JSONDecodeError:
                print(f"Failed to parse {filename}")

    return results


def main():
    # Set the folder path where your JSON files are stored
    target_folder = "../data/marquee"

    data_points = process_folder(target_folder)

    if data_points:
        df = pd.DataFrame(data_points)
        output_file = "url_verification_report.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Report generated: {output_file}")
    else:
        print("No data found to process.")


if __name__ == "__main__":
    main()
