import requests
import os
import time

# Configuration
BASE_URL = "https://phl.carto.com/api/v2/sql"
START_YEAR = 2006
END_YEAR = 2025
OUTPUT_DIR = "data/raw/philly_crime_data"
MAX_RETRIES = 3

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def download_month(year, month):
    month_str = f"{month:02d}"
    file_path = os.path.join(OUTPUT_DIR, f"incidents_{year}_{month_str}.csv")

    # Check if file already exists to save time/bandwidth
    if os.path.exists(file_path):
        print(f"Skipping {year}-{month_str} (Already exists).")
        return True

    start_date = f"{year}-{month_str}-01"
    end_date = f"{year + 1}-01-01" if month == 12 else f"{year}-{(month + 1):02d}-01"

    query = f"SELECT * FROM incidents_part1_part2 WHERE dispatch_date_time >= '{start_date}' AND dispatch_date_time < '{end_date}'"
    params = {"q": query, "format": "csv"}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Downloading {year}-{month_str} (Attempt {attempt})...")
            response = requests.get(BASE_URL, params=params, timeout=120)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Successfully saved {file_path}")
            return True

        except Exception as e:
            print(f"   Attempt {attempt} failed for {year}-{month_str}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                print(
                    f"!!! Giving up on {year}-{month_str} after {MAX_RETRIES} attempts."
                )
                return False


# Execution
for year in range(START_YEAR, END_YEAR + 1):
    for month in range(1, 13):
        success = download_month(year, month)
        if success:
            time.sleep(1)  # Be a good API citizen

print("\nProcess finished. Check your 'philly_crime_data' folder!")
