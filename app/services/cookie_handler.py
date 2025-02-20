from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.core.interfaces import ICookieHandler
from app.core.exceptions import CookieConsentError
from app.core.config import Config
from app.utils.utils import random_sleep

class CookieHandler(ICookieHandler):
    def __init__(self, driver, screenshot_manager):
        self.driver = driver
        self.screenshot_manager = screenshot_manager
    
    def handle_cookie_consent(self) -> bool:
        """Handle cookie consent by simulating button clicks"""
        try:
            # Take screenshot before handling cookies
            self.screenshot_manager.take_screenshot("before_cookies")
            
            # Wait for page to be fully loaded
            random_sleep(2, 3)
            
            # Try to find and click the cookie consent button with explicit wait
            for selector in Config.COOKIE_BUTTON_SELECTORS:
                try:
                    print(f"Looking for cookie button with selector: {selector}")
                    # Wait up to 5 seconds for each selector
                    wait = WebDriverWait(self.driver, 5)
                    buttons = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    
                    for button in buttons:
                        if button.is_displayed():
                            print(f"Found visible button with selector: {selector}")
                            # Wait for button to be clickable
                            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            button.click()
                            print(f"Clicked button with selector: {selector}")
                            random_sleep(1, 2)
                            return True
                except Exception as e:
                    print(f"Failed with selector {selector}: {str(e)}")
                    continue
            
            # If no cookie banner found, it might be already accepted or not present
            print("No cookie banner found - might be already accepted or not present")
            return True
                
        except Exception as e:
            raise CookieConsentError(f"Error handling cookie consent: {str(e)}")
