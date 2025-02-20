import os
from datetime import datetime
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from app.core.interfaces import IScreenshotManager
from app.core.exceptions import ScreenshotError
from app.core.config import Config


class ScreenshotManager(IScreenshotManager):
    def __init__(self, driver, profile_id: str):
        self.driver = driver
        self.profile_id = profile_id
        self.profile_dir = self._get_profile_dir()
        self.screenshot_dir = self._get_screenshot_dir()
        self._ensure_dirs()
    
    def _get_profile_dir(self) -> str:
        """Get the profile directory path"""
        return Config.PROFILE_DIR_TEMPLATE.format(
            base_dir=Config.BASE_DIR,
            profile_id=self.profile_id
        )
    
    def _get_screenshot_dir(self) -> str:
        """Get the screenshot directory path"""
        return Config.SCREENSHOT_DIR_TEMPLATE.format(
            base_dir=Config.BASE_DIR,
            profile_id=self.profile_id
        )
    
    def _ensure_dirs(self):
        """Create all necessary directories if they don't exist"""
        os.makedirs(self.profile_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def take_screenshot(self, name: str) -> Optional[str]:
        """Take a screenshot and save it with timestamp"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.screenshot_dir}/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved as: {filename}")
            return filename
        except Exception as e:
            raise ScreenshotError(f"Error taking screenshot: {str(e)}")
