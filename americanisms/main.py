import re
import requests

from common.environment_variable import EnvironmentVariable

# Configuration
SITE_URL = "https://biddenham.org.uk"  # No trailing slash

PASSWORD = EnvironmentVariable("WORDPRESS_APPLICATION_KEY").value
USERNAME = EnvironmentVariable("WORDPRESS_USERNAME").value

# POST_TYPE = "pages"  # Change to "posts" when ready
POST_TYPE = "posts"  # Change to "posts" when ready
OUTPUT_FILE = "americanisms/output/scan_results.txt"


# Define regex patterns for scanning
SCAN_PATTERNS = {
    "American Spelling (orize/orise)": r"\b\w+ize[sd]?\b",
    "American Spelling (color/colour)": r"\bcolor(?:s|ed|ful)?\b",
    "Em-dash usage": r"—",
    "Potential AI phrase (delve)": r"\bdelve\b",
    "Potential AI phrase (tapestry)": r"\btapestry\b",
    "Potential AI phrase (testament)": r"\ba testament to\b",
}

EXCEPTIONS = [
    "flexsize",
    "fontsize",
    "prize",
    "prizes",
    "prized",
    "resized",
    "seized",
    "size-full",
    "size-large",
    "size",
    "sized",
    "sizes",
    "sizeslug",
    "whitespace_size",
]


def fetch_wp_data(endpoint_type, auth, base_url):
    """Fetches all items for a given post type with pagination."""
    url = f"{base_url}/wp-json/wp/v2/{endpoint_type}"
    params = {"per_page": 100, "page": 1, "context": "edit"}

    all_items = []

    while True:
        response = requests.get(url, params=params, auth=auth)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        all_items.extend(data)

        # Check total pages from headers
        total_pages = int(response.headers.get("X-WP-TotalPages", 1))
        if params["page"] >= total_pages:
            break

        params["page"] += 1

    return all_items


def scan_content(items, patterns):
    """Scans item titles and content for specific patterns."""
    flagged_report = []

    for item in items:
        item_id = item.get("id")
        title = item.get("title", {}).get("rendered", "")
        content = item.get("content", {}).get("raw", "")
        link = item.get("link", "")

        text_to_scan = f"{title} {content}"
        matches_found = {}

        for label, pattern in patterns.items():
            matches = re.findall(pattern, text_to_scan, flags=re.IGNORECASE)
            if matches:
                matches_list = [match for match in set(matches) if match.lower() not in EXCEPTIONS]

                # matches_found[label] = list(set(matches))
                matches_found[label] = matches_list

        if matches_found:
            flagged_report.append(
                {
                    "id": item_id,
                    "title": title,
                    "link": link,
                    "issues": matches_found,
                }
            )

    return flagged_report


def write_report_to_file(results, filename):
    """Writes the flagged results into a structured text file."""
    with open(filename, "w+", encoding="utf-8") as f:
        f.write(f"WordPress Scan Report ({POST_TYPE.capitalize()})\n")
        f.write(f"Total entries with issues found: {len(results)}\n")
        f.write("=" * 60 + "\n\n")

        for entry in results:
            f.write(f"Title: {entry['title']} (ID: {entry['id']})\n")
            f.write(f"URL:   {entry['link']}\n")
            f.write("Matches found:\n")
            for issue, items in entry["issues"].items():
                # Format list of items neatly for the text file
                items_str = ", ".join([f"'{i}'" for i in items])
                f.write(f"  - {issue}: {items_str}\n")
            f.write("-" * 60 + "\n\n")


def main():
    auth = (USERNAME, PASSWORD)

    print(f"Starting fetch for {POST_TYPE}...")
    wp_items = fetch_wp_data(POST_TYPE, auth, SITE_URL)

    print(f"Fetched {len(wp_items)} items. Beginning scan...")
    results = scan_content(wp_items, SCAN_PATTERNS)

    print(f"Writing results to {OUTPUT_FILE}...")
    write_report_to_file(results, OUTPUT_FILE)
    print("Done.")


if __name__ == "__main__":
    main()
