import json

from app.services.malt_scrapper import MaltScraper
            
if __name__ == '__main__':
    scraper = MaltScraper(headless=False, profil_url='https://malt.fr/profile/yacinebenkhedimallah')
    result = scraper.extract_profile_data()
    print("\nFinal Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False))