import requests
from bs4 import BeautifulSoup
import csv
import sys
# import re


def main():
    teams = {
        "208126": "Biddenham CC - Under 9",
        "79562": "Biddenham CC - Sunday League XI",
        "35361": "Biddenham CC - Sunday Friendly XI",
        "286729": "Biddenham CC - Midweek XI",
        "62235": "Biddenham CC - Under 11",
        "208125": "Biddenham CC - Under 11 B",
        "167823": "Biddenham CC - Under 13",
        "260976": "Biddenham CC - Under 13 B",
        "70010": "Biddenham CC - Under 15",
    }
    fixtures_list = []
    for team, team_name in teams.items():
        base_url = "https://biddenham.play-cricket.com/Matches"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        # Iterate through months May (5) to September (9)
        for month in range(5, 10):
            params = {
                "tab": "Fixture",
                "selected_season_id": "259",
                "seasonchange": "f",
                "fixture_month": month,
                "season_id": "259",
                "team_id": team,
                "view_by": "month",
                "home_or_away": "both",
            }

            response = requests.get(base_url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"Failed to retrieve data for month {month}")
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all match cards/rows
            match_tbcs = soup.find_all("div", class_="match-tbc")
            current_date = "xxx"
            if len(match_tbcs) > 0:
                match_tbc = match_tbcs[0]
                tab_panes = match_tbc.find_all("div", class_="tab-pane")
                if not tab_panes:
                    sys.exit()

                tab_pane = tab_panes[0]
                matches = tab_pane.select(":scope > .col-sm-12.title2, :scope > .col-sm-12.card-table")
                if not matches:
                    continue
                    # sys.exit()
                for match in matches:
                    # Check if 'title2' is one of the classes for this element
                    if "title2" in match.get("class", []):
                        current_date = match.get_text(strip=True)
                        print(f"Found Date Header: {current_date}")
                        continue  # Move to the next element in the loop

                    # If it is not a title2 element, it must be a card-table element
                    if "card-table" in match.get("class", []):
                        if current_date:
                            print(f"Processing fixture for date: {current_date}")
                            # You can now proceed to extract the home team, away team,
                            # venue, and time from this card-table element, using
                            # the current_date variable for the CSV row.

                            # Get teams
                            teams = match.find_all("p", class_="txt1")
                            if len(teams) > 1:
                                team1 = teams[0].get_text(strip=True)
                                team2 = teams[1].get_text(strip=True)

                            # Get location
                            locations = match.find_all("p", class_="location")
                            if len(locations) > 0:
                                location = locations[0].get_text(strip=True)

                            # Get time
                            times = match.find_all("p", class_="time")
                            if len(times) > 0:
                                time = times[0].get_text(strip=True)
                            _ = 1

                            if not location:
                                location = "Biddenham Pavilion"
                            if team1 and team2 and location and time:
                                fixtures_list.append(
                                    {
                                        "stratum": team_name,
                                        "home team": team1,
                                        "away team": team2,
                                        "venue": location,
                                        "date": current_date,
                                        "time": time,
                                    }
                                )

                _ = 1
            else:
                sys.exit()
            _ = 1

    # Export to CSV
    keys = ["stratum", "home team", "away team", "venue", "date", "time"]
    with open("biddenham_cricket_fixtures/resources/data/biddenham_fixtures.csv", "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(fixtures_list)

    print(f"Successfully exported {len(fixtures_list)} fixtures to biddenham_fixtures.csv")


if __name__ == "__main__":
    main()
