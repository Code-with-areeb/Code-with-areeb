import os
import json
import requests
from bs4 import BeautifulSoup

# USERNAME UPDATE HERE
USERNAME = "Code-with-areeb"  # ya jo tumhara actual GitHub handle ho

def fetch_contributions():
    url = f"https://github.com/users/{USERNAME}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch contributions: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    days = []
    
    # Extract day elements
    for td in soup.find_all('td', class_='ContributionCalendar-day'):
        date = td.get('data-date')
        level = td.get('data-level', '0')
        if date:
            days.append({
                "date": date,
                "level": int(level)
            })

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump({"total": len(days), "days": days}, f, indent=2)
        
    print(f"Fetched {len(days)} contribution days and saved to data/contributions.json")

if __name__ == "__main__":
    fetch_contributions()render_heatmap_svg.py