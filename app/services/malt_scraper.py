import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app.utils.utils import random_sleep
from app.services.screenshot_manager import ScreenshotManager
from app.services.html_manager import HTMLManager as HtmlManager
from app.services.cookie_handler import CookieHandler
from app.services.data_extractor import MaltDataExtractor as DataExtractor
from app.core.config import Config
import re

class MaltScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        
    def _setup_driver(self):
        """Setup and configure the undetected Chrome driver"""
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
            
        # Add all browser arguments from config
        for arg in Config.BROWSER_ARGS:
            options.add_argument(arg)
            
        # Create and configure the undetected Chrome driver
        self.driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            browser_executable_path=None,
            suppress_welcome=True,
            use_subprocess=True
        )
        
        # Set window size
        self.driver.set_window_size(*Config.WINDOW_SIZE)
        
        return self.driver
        
    def _handle_cloudflare(self):
        """Handle Cloudflare challenge if present"""
        for selector in Config.CLOUDFLARE_SELECTORS:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    print("Detected Cloudflare challenge, waiting for it to complete...")
                    random_sleep(Config.CLOUDFLARE_MIN_SLEEP, Config.CLOUDFLARE_MAX_SLEEP)
                    break
            except TimeoutException:
                continue
                
    def _extract_profile_id(self, url: str) -> str:
        """Extract profile ID from URL"""
        match = re.search(r'profile/([^/]+)', url)
        if not match:
            raise ValueError(f"Could not extract profile ID from URL: {url}")
        return match.group(1)
    
    def scrape_profile(self, url: str) -> dict:
        """Scrape a Malt profile"""
        try:
            # Initialize driver if not already initialized
            if not self.driver:
                self.driver = self._setup_driver()
            
            # Extract profile ID from URL
            profile_id = self._extract_profile_id(url)
            
            # Initialize managers
            screenshot_manager = ScreenshotManager(self.driver, profile_id)
            html_manager = HtmlManager(self.driver, profile_id)
            cookie_handler = CookieHandler(self.driver, screenshot_manager)
            data_extractor = DataExtractor(self.driver, screenshot_manager, cookie_handler)
            
            # Navigate to URL
            print(f"Navigating to {url}...")
            self.driver.get(url)
            random_sleep()
            
            # Take initial screenshot
            screenshot_manager.take_screenshot("initial_page")
            
            # Handle cookie consent
            print("\nHandling cookie consent...")
            cookie_handler.handle_cookie_consent()
            
            # Handle Cloudflare if present
            self._handle_cloudflare()
            
            # Print debug information
            print("\nPage Information:")
            print("Title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            
            # Wait for Vue.js to finish rendering
            print("Waiting for Vue.js to finish rendering...")
            random_sleep()
            
            # Save page HTML
            print("Saving page HTML...")
            html_manager.save_page_source()
            
            # Extract and return profile data
            return data_extractor.extract_profile_data(url)
            
        except Exception as e:
            print(f"Error scraping profile: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

def print_profile_data(data: dict):
    """Print profile data in a readable format"""
    if not data:
        print("No data available")
        return
        
    print("\nProfile Data:")
    print("=" * 50)
    print("\nBasic Information:")
    print("Name:", data.get('name', ''))
    print("Title:", data.get('title', ''))
    print("Location:", data.get('location', ''))
    print("Rate:", data.get('rate', ''))
    
    print("\nDescription:")
    description = data.get('description', [])
    if isinstance(description, list):
        for item in description:
            print("-", item)
    else:
        print(description)
    
    print("\n" + "=" * 50)
