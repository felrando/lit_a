import requests
import csv

def get_country_codes():
    url = "https://datahub.io/core/country-list/r/data.csv"
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.reader(lines)
    next(reader)  # Skip header
    country_codes = {row[0]: row[1] for row in reader if len(row) >= 2}
    return country_codes

def main():
    country_codes = get_country_codes()
    print("Country codes retrieved:")
    for country, code in country_codes.items():
        print(f"{country}: {code}")

if __name__ == "__main__":
    main()