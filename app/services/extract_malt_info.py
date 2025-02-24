from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random


class ExtractMaltInfo:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, by, value, timeout=20):
        """Wait for an element and return it once found"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            # Save page source for debugging
            try:
                with open(self.workspace_path + "/page_source.html", "w") as f:
                    f.write(self.driver.page_source)
                print(
                    "Page source saved to " + self.workspace_path + "/page_source.html"
                )
            except Exception as e:
                print(f"Failed to save page source: {str(e)}")
            raise

    def extract(self) -> Dict[str, Any]:
        try:
            # Try to find any element that would indicate the page loaded
            self.wait_for_element(By.TAG_NAME, "body")
            print("Body element found")
        except TimeoutException:
            print("Failed to find body element")
            raise

        # Print current URL to verify redirect
        print(f"Current URL: {self.driver.current_url}")

        # Wait for main content
        print("Waiting for profile header...")
        self.wait_for_element(By.CLASS_NAME, "profile-header__grid")
        print("Profile header found")

        # Extract basic info
        print("Extracting basic info...")
        fullname = self.wait_for_element(
            By.CLASS_NAME, "profile-headline-read-fullname"
        ).text
        title = self.wait_for_element(
            By.CLASS_NAME, "profile-headline-read-headline"
        ).text

        # Extract other fields with proper error handling
        daily_rate = None
        try:
            daily_rate = self.wait_for_element(
                By.CLASS_NAME, "block-list__price"
            ).text.strip()
        except TimeoutException:
            print("Daily rate not found")

        # extract response rate
        response_rate = None
        try:
            response_rate = self.wait_for_element(
                By.CSS_SELECTOR,
                "[data-testid='answer-rate-indicator'] .profile-indicators-content",
            ).text.strip()
        except TimeoutException:
            print("Response rate not found")

        experience_years = None
        try:
            experience_years = self.wait_for_element(
                By.CSS_SELECTOR,
                "[data-testid='profile-level-indicator'] .profile-indicators-content",
            ).text.strip()
        except TimeoutException:
            print("Experience years not found")

        image_url = None
        try:
            image_url = self.wait_for_element(
                By.CSS_SELECTOR, ".profile-photo_wrapper img"
            ).get_attribute("src")
        except TimeoutException:
            print("Image URL not found")

        # Extract skills
        top_skills = []
        skills = []
        try:
            skills_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="profile-main-skill-set-top-skills-list"] .profile-edition__skills_item__tag__link__content',
            )
            top_skills = [skill.text for skill in skills_elements]
            skills_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="profile-main-skill-set-selected-skills-list"] .profile-edition__skills_item__tag__link__content',
            )
            skills = [skill.text for skill in skills_elements]
        except:
            print("Skills not found")

        # Extract locations
        location = None
        try:
            location_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='profile-location-preference-address']"
            )
            location = [location.text for location in location_elements]
        except:
            print("Location not found")

        # Extract work locations
        work_locations = []
        try:
            work_locations_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".profile-workplace-preferences__item li"
            )
            work_locations = [location.text for location in work_locations_elements]
        except:
            print("Work locations not found")

        # Extract languages
        expertise_domains = []
        try:
            expertise_domains_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".profile-skills-read-only .profile-edition__skills_item__tag__link__content",
            )
            expertise_domains = [domain.text for domain in expertise_domains_elements]
        except:
            print("Expertise domains not found")

        # Extract certifications
        certifications = []
        try:
            certifications_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".profile-certifications__list-item__main-content-title",
            )
            certifications = [
                {
                    "name": certification.text,
                    "date": None,
                    "description": None,
                }
                for certification in certifications_elements
            ]
        except:
            print("Certifications not found")

        # Extract availability
        availability: bool = None
        try:
            availability_text = self.wait_for_element(
                By.CLASS_NAME, "joy-availability", timeout=5
            ).get_attribute("title")
            availability = availability_text == "Disponibilité confirmée"
        except TimeoutException:
            print("Availability not found")

        # Extract languages
        languages = []
        try:
            languages_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".profile-languages__item__title"
            )
            languages = [
                {"name": language.text, "level": None}
                for language in languages_elements
            ]
        except:
            print("Languages not found")

        # Categories
        categories = []
        try:
            categories_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".categories__list-item .joy-link__text"
            )
            categories = [category.text for category in categories_elements]
        except:
            print("Categories not found")

        # Extract missions count
        missions_count = None
        try:
            missions_count = len(
                self.driver.find_elements(
                    By.CLASS_NAME, "profile-experiences__list-item"
                )
            )
        except TimeoutException:
            print("Missions count not found")

        # Extract description
        description = None
        try:
            description = self.wait_for_element(
                By.CSS_SELECTOR, '[data-testid="profile-description"]', timeout=5
            ).text.strip()
        except TimeoutException:
            print("Description not found")

        print(f"Extraction completed for: {fullname}")

        return {
            "fullname": fullname,
            "title": title,
            "categories": categories,
            "daily_rate": daily_rate,
            "response_rate": response_rate,
            "experience_years": experience_years,
            "image_url": image_url,
            "top_skills": top_skills,
            "skills": skills,
            "location": location,
            "work_locations": work_locations,
            "languages": languages,
            "availability": availability,
            "expertise_domains": expertise_domains,
            "missions_count": missions_count,
            "description": description,
            "certifications": certifications,
        }
