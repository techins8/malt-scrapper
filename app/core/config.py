from typing import List
import os

class Config:
    # Base directory for all data
    BASE_DIR = 'var/malt'
    
    # Directory templates (will be formatted with profile_id)
    PROFILE_DIR_TEMPLATE = os.path.join(BASE_DIR, '{profile_id}')
    SCREENSHOT_DIR_TEMPLATE = os.path.join(BASE_DIR, '{profile_id}', 'screenshots')
    HTML_FILE_TEMPLATE = os.path.join(BASE_DIR, '{profile_id}', 'profile_{timestamp}.html')
    
    # Browser settings
    BROWSER_ARGS = [
        '--window-size=1920,1080',
        '--no-sandbox',
        '--disable-gpu',
        '--lang=fr-FR',
        '--accept-language=fr-FR,fr;q=0.9,en;q=0.8',
        '--disable-blink-features=AutomationControlled'
    ]
    
    # Cookie consent selectors
    COOKIE_BUTTON_SELECTORS: List[str] = [
        'button[data-testid="cookie-banner-accept-button"]',
        '#onetrust-accept-btn-handler',
        '.cookie-accept',
        'button.accept-cookies',
        'button[data-testid="cookie-notice-accept-button"]',
        '#accept-cookies',
        '.accept-all-cookies',
        'button.back-button',
        '#didomi-notice-agree-button',
        'button[aria-label="Accepter"]',
        'button[aria-label="Accept"]',
        '.didomi-components-button',
        '#acceptAllCookies',
        '.js-cookies-accept',
        'button.accept-all',
        'button.cookies-accept',
        '.cookie-consent__accept-button'
    ]
    
    # Cloudflare selectors
    CLOUDFLARE_SELECTORS: List[str] = [
        '#challenge-running',
        '#cf-challenge-running',
        '.cf-browser-verification',
        '#cf-content'
    ]
    
    # Sleep intervals
    MIN_SLEEP = 2
    MAX_SLEEP = 5
    CLOUDFLARE_MIN_SLEEP = 15
    CLOUDFLARE_MAX_SLEEP = 20
    WINDOW_SIZE = (1920, 1080)
