import undetected_chromedriver as uc
from interfaces import IWebDriver
from exceptions import WebDriverInitError
from config import Config

class ChromeDriverManager(IWebDriver):
    def __init__(self):
        self.driver = None
    
    def start_driver(self, headless: bool = False):
        try:
            options = uc.ChromeOptions()
            
            if headless:
                options.add_argument('--headless=new')
            
            # Add browser arguments from config
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
            
        except Exception as e:
            raise WebDriverInitError(f"Failed to initialize WebDriver: {str(e)}")
    
    def quit(self):
        if self.driver:
            self.driver.quit()
