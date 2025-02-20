import json
import os
from app.services.malt_scraper import MaltScraper, print_profile_data

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('var/malt/yacinebenkhedimallah', exist_ok=True)
    
    scraper = MaltScraper(headless=False)
    url = 'https://malt.fr/profile/yacinebenkhedimallah'
    result = scraper.scrape_profile(url)
    print_profile_data(result)
    
    # Also save the raw data as JSON
    with open('var/malt/yacinebenkhedimallah/profile_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)