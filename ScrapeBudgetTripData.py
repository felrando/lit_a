import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime

# Base URL for budget data
BASE_URL = "https://www.budgetyourtrip.com/budgetreportadv.php"

# Budget types mapping (1 = Budget, 2 = Mid-Range, 3 = Luxury)
BUDGET_TYPES = {1: "Budget", 2: "Mid-Range", 3: "Luxury"}

# Set up a requests session with retries
def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retry))
    return session

# Scrape budget data for Canada
def scrape_budget_data():
    session = get_session()
    country_code = "CA"  # Canada
    all_data = []
    scrape_date = datetime.now().strftime("%Y-%m-%d")
    
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
            print(f"Scraping response for {budget_name} (Canada)")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for Canada ({budget_name}): {e}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        cost_span = soup.find("span", class_="curvalue")
        if not cost_span:
            print(f"No data found for Canada - {budget_name}")
            continue
        
        cost = cost_span.text.strip()
        all_data.append({
            "Country": "Canada",
            "Budget Type": budget_name,
            "Category": "Average Daily Cost",
            "Cost": cost,
            "Date": scrape_date
        })
        
        time.sleep(random.uniform(1, 3))  # Randomized delay to avoid detection
    
    return all_data

# Main script to scrape data for Canada
def main():
    data = scrape_budget_data()
    if data:
        df = pd.DataFrame(data)
        df.to_csv("canada_budget_data.csv", index=False)
        print("Data saved to canada_budget_data.csv")
    else:
        print("No data collected for Canada.")

if __name__ == "__main__":
    main()




