import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base_dir)

from app.services.malt_scrapper import MaltScrapper

if __name__ == "__main__":
    id: str = "yacinebenkhedimallah"
    scraper = MaltScrapper(
        headless=False,
        profil_url=f"https://malt.fr/profile/{id}",
    )
    result = scraper.extract_profile_data()
    print("\nFinal Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
