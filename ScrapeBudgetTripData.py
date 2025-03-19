import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
import calendar

# Base URL for budget data
BASE_URL = "https://www.budgetyourtrip.com/budgetreportadv.php"

# Budget types mapping (1 = Budget, 2 = Mid-Range, 3 = Luxury)
BUDGET_TYPES = {1: "Budget", 2: "Mid-Range", 3: "Luxury"}

# Function to retrieve country codes from Google public dataset
def get_country_codes():
    url = "https://datahub.io/core/country-list/r/data.csv"
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.reader(lines)
    next(reader)  # Skip header
    country_codes = {row[0]: row[1] for row in reader if len(row) >= 2}
    return country_codes

# Set up a requests session with retries
def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retry))
    return session

# Scrape budget data for a given country
def scrape_budget_data(country, country_code):
    session = get_session()
    all_data = []
    scrape_date = datetime.now().strftime("%Y-%m-%d")
    today_name = calendar.day_name[datetime.now().weekday()]
    
    for budget_type, budget_name in BUDGET_TYPES.items():
        params = {
            "geonameid": "",
            "countrysearch": "",
            "country_code": country_code,
            "categoryid": 0,
            "budgettype": budget_type,
            "triptype": 0,
            "startdate": "",
            "enddate": "",
            "travelerno": 0
        }
        headers = {"User-Agent": UserAgent().random}
        
        try:
            response = session.get(BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Scraping response for {budget_name} ({country})")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {country} ({budget_name}): {e}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        cost_span = soup.find("span", class_="curvalue")
        if not cost_span:
            print(f"No data found for {country} - {budget_name}")
            continue
        
        cost = cost_span.text.strip()
        print(f"{today_name}, {scrape_date}: {country} ({budget_name}) - {cost}")
        
        all_data.append({
            "Country Code": country_code,
            "Country Name": country,
            "Budget Type": budget_name,
            "Category": "Average Daily Cost",
            "Cost": cost,
            "Date": scrape_date,
            "Day": today_name
        })
        
        time.sleep(random.uniform(1, 3))  # Randomized delay to avoid detection
    
    return all_data

# Main script to scrape all data
def main():
    country_codes = get_country_codes()
    print("Country codes retrieved:")
    for country, code in country_codes.items():
        print(f"{country}: {code}")
    
    all_data = []
    
    for country, code in country_codes.items():
        print(f"Scraping {country}...")
        data = scrape_budget_data(country, code)  # This function already loops through budget types
        if data:
            all_data.extend(data)
        time.sleep(random.uniform(1, 3))
    
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("budget_data.csv", index=False)
        print("Data saved to budget_data.csv")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
