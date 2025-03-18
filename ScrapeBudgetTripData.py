import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Base URL for budget data
BASE_URL = "https://www.budgetyourtrip.com/budgetreportadv.php"

# Budget types mapping (1 = Budget, 2 = Mid-Range, 3 = Luxury)
BUDGET_TYPES = {1: "Budget", 2: "Mid-Range", 3: "Luxury"}

# List of proxy servers (you need to provide a working list)
PROXIES = [
    "http://proxy1:port",
    "http://proxy2:port",
    "http://proxy3:port"
]

# Get country codes from Google public dataset
def get_country_codes():
    url = "https://developers.google.com/public-data/docs/canonical/countries_csv"
    response = requests.get(url)
    lines = response.text.split("\n")[1:]  # Skip header
    country_codes = {}
    
    for line in lines:
        parts = line.split(",")
        if len(parts) >= 2:
            country_name = parts[1].strip().replace(" ", "-")  # Replace spaces with dashes
            country_code = parts[0].strip()
            country_codes[country_name] = country_code
    
    return country_codes

# Set up a requests session with retries
def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retry))
    return session

# Scrape budget data for a specific country and budget type
def scrape_budget_data(country_code, budget_type):
    session = get_session()
    params = {
        "country_code": country_code,
        "budgettype": budget_type
    }
    headers = {"User-Agent": UserAgent().random}
    proxy = {"http": random.choice(PROXIES), "https": random.choice(PROXIES)}
    
    response = session.get(BASE_URL, params=params, headers=headers, proxies=proxy)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the table data
    table = soup.find("table", class_="report")
    if not table:
        return None
    
    rows = table.find_all("tr")[1:]  # Skip header row
    budget_data = []
    for row in rows:
        cols = row.find_all("td")
        category = cols[0].text.strip()
        cost = cols[1].text.strip()
        budget_data.append({"Category": category, "Cost": cost})
    
    return budget_data

# Main script to scrape all data
def main():
    country_codes = get_country_codes()
    all_data = []
    
    for country, code in country_codes.items():
        for budget_type, budget_name in BUDGET_TYPES.items():
            print(f"Scraping {country} - {budget_name}...")
            data = scrape_budget_data(code, budget_type)
            if data:
                for entry in data:
                    all_data.append({
                        "Country": country,
                        "Budget Type": budget_name,
                        "Category": entry["Category"],
                        "Cost": entry["Cost"]
                    })
            time.sleep(random.uniform(1, 3))  # Randomized delay to avoid detection
    
    # Save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv("budget_data.csv", index=False)
    print("Data saved to budget_data.csv")

if __name__ == "__main__":
    main()
