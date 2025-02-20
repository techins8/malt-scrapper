from abc import ABC, abstractmethod
from typing import Optional

class IWebDriver(ABC):
    @abstractmethod
    def start_driver(self, headless: bool = False):
        pass

    @abstractmethod
    def quit(self):
        pass

class IScreenshotManager(ABC):
    @abstractmethod
    def __init__(self, driver, profile_id: str):
        pass

    @abstractmethod
    def take_screenshot(self, name: str) -> Optional[str]:
        pass

class ICookieHandler(ABC):
    @abstractmethod
    def handle_cookie_consent(self) -> bool:
        pass

class IDataExtractor(ABC):
    @abstractmethod
    def extract_profile_data(self, url: str) -> dict:
        pass
