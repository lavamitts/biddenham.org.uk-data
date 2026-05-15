import requests
from bs4 import BeautifulSoup
import csv
import re


def scrape_fixtures():
    base_url = "https://biddenham.play-cricket.com/Matches"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    fixtures_list = []

    # Iterate through months May (5) to September (9)
    for month in range(5, 10):
        params = {
            "tab": "Fixture",
            "selected_season_id": "259",
            "seasonchange": "f",
            "fixture_month": month,
            "season_id": "259",
            "team_id": "79562",
            "view_by": "month",
            "home_or_away": "both",
        }

        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve data for month {month}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all match cards/rows
        # Play-Cricket usually wraps matches in 'div' elements with specific classes
        matches = soup.find_all("div", class_="match_card")

        if not matches:
            print(f"No more fixtures found starting from month {month}.")
            break

        for match in matches:
            # Extracting teams
            teams = match.find_all("div", class_="team_name")
            if len(teams) >= 2:
                home_team = teams[0].get_text(strip=True)
                away_team = teams[1].get_text(strip=True)
            else:
                continue

            # Extracting venue
            venue_element = match.find("p", class_="location")
            venue = venue_element.get_text(strip=True) if venue_element else "Unknown"

            # Extracting date and time
            # Dates are often in a <span> or <div> within the match header
            date_element = match.find("div", class_="match_date")
            time_element = match.find("div", class_="match_time")

            match_date = date_element.get_text(strip=True) if date_element else ""
            match_time = time_element.get_text(strip=True) if time_element else ""

            fixtures_list.append({"home team": home_team, "away team": away_team, "venue": venue, "date": match_date, "time": match_time})

    # Export to CSV
    keys = ["home team", "away team", "venue", "date", "time"]
    with open("biddenham_fixtures.csv", "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(fixtures_list)

    print(f"Successfully exported {len(fixtures_list)} fixtures to biddenham_fixtures.csv")


if __name__ == "__main__":
    scrape_fixtures()
