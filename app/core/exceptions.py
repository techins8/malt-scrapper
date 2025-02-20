class WebDriverInitError(Exception):
    """Raised when there's an error initializing the WebDriver"""
    pass

class ScreenshotError(Exception):
    """Raised when there's an error taking a screenshot"""
    pass

class CookieConsentError(Exception):
    """Raised when there's an error handling cookie consent"""
    pass

class DataExtractionError(Exception):
    """Raised when there's an error extracting data from the profile"""
    pass
