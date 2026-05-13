from datetime import datetime, timedelta


def first_tuesdays(start_year=2021):
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    result = []

    # Loop through each year and month
    for year in range(start_year, current_year + 1):
        for month in range(1, 13):
            if year == current_year and month > current_month:
                break  # Don't go past the current month

            # Start on the 1st of the month
            date = datetime(year, month, 1)

            # Find the first Tuesday (weekday 1 = Tuesday)
            while date.weekday() != 1:
                date += timedelta(days=1)

            result.append(date.strftime('%Y-%m-%d'))

    return result


# Print the results
for tuesday in first_tuesdays():
    print(tuesday)
