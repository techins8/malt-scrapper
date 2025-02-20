import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import json
import os
from datetime import datetime

class MaltScraper:
    def __init__(self, headless=False):
        self.headless = headless
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = 'screenshots'
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def take_screenshot(self, name):
        """Take a screenshot and save it with timestamp"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.screenshot_dir}/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved as: {filename}")
            return filename
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None
    
    def start_driver(self):
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
            
        # Essential settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # Set language
        options.add_argument('--lang=fr-FR')
        options.add_argument('--accept-language=fr-FR,fr;q=0.9,en;q=0.8')
        
        # Try to look more like a real browser
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Create and configure the undetected Chrome driver
        self.driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            browser_executable_path=None,
            suppress_welcome=True,
            use_subprocess=True
        )
        
        # Set window size
        self.driver.set_window_size(1920, 1080)
        
        return self.driver
    
    def random_sleep(self, min_seconds=2, max_seconds=5):
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def handle_cookie_consent(self):
        """Handle cookie consent by simulating button clicks"""
        try:
            # Take screenshot before handling cookies
            self.take_screenshot("before_cookies")
            
            # Try to find and click the cookie consent button
            cookie_button_selectors = [
                'button[data-testid="cookie-banner-accept-button"]',
                '#onetrust-accept-btn-handler',
                '.cookie-accept',
                'button.accept-cookies',
                'button[data-testid="cookie-notice-accept-button"]',
                '#accept-cookies',
                '.accept-all-cookies',
                'button.back-button'
            ]
            
            for selector in cookie_button_selectors:
                try:
                    print(f"Looking for cookie button with selector: {selector}")
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed():
                            print(f"Found visible button with selector: {selector}")
                            button.click()
                            print(f"Clicked button with selector: {selector}")
                            self.random_sleep(1, 2)
                            return True
                except Exception as e:
                    print(f"Failed with selector {selector}: {str(e)}")
                    continue
            
            return False
                
        except Exception as e:
            print(f"Error handling cookie consent: {str(e)}")
        return False
    
    def extract_profile_data(self, url):
        try:
            self.driver = self.start_driver()
            
            # Navigate to URL
            print(f"Navigating to {url}...")
            self.driver.get(url)
            self.random_sleep(3, 6)
            
            # Take initial screenshot
            self.take_screenshot("initial_page")
            
            # Handle cookie consent
            print("\nHandling cookie consent...")
            self.handle_cookie_consent()
            
            # Print debug information
            print("\nPage Information:")
            print("Title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            
            # Wait for content to load and check for Cloudflare
            print("\nWaiting for page content to load...")
            try:
                # First check if we're on a Cloudflare page
                cloudflare_selectors = [
                    '#challenge-running',
                    '#cf-challenge-running',
                    '.cf-browser-verification',
                    '#cf-content'
                ]
                
                for selector in cloudflare_selectors:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if element.is_displayed():
                            print("Detected Cloudflare challenge, waiting for it to complete...")
                            self.random_sleep(15, 20)
                            break
                    except TimeoutException:
                        continue
                
                # Wait for Vue.js to finish rendering
                print("Waiting for Vue.js to finish rendering...")
                self.random_sleep(10, 15)
                
                # Execute JavaScript to extract content
                js_script = """
                    function getTextContent(element, selector) {
                        const el = element.querySelector(selector);
                        return el ? el.innerText.trim() : '';
                    }
                    
                    function getAllText(elements) {
                        return Array.from(elements).map(el => el.innerText.trim()).filter(text => text);
                    }
                    
                    function cleanText(text) {
                        return text.replace(/\\s+/g, ' ').trim();
                    }
                    
                    function normalizeSkill(skill) {
                        // Normalize common variations
                        const normalizations = {
                            'Control M': 'Control-M',
                            'Control-M': 'Control-M',
                            'ControlM': 'Control-M',
                            'API Management': 'API',
                            'API': 'API',
                            'REST API': 'REST',
                            'RESTful': 'REST',
                            'SOAP API': 'SOAP',
                            'Web Services': 'Web Services',
                            'Webservices': 'Web Services',
                            'SQL Server': 'Microsoft SQL Server',
                            'MSSQL': 'Microsoft SQL Server',
                            'Microsoft SQL': 'Microsoft SQL Server'
                        };
                        
                        return normalizations[skill] || skill;
                    }
                    
                    // Wait for content to be available
                    const waitForElement = (selector, timeout = 5000) => {
                        const start = Date.now();
                        return new Promise((resolve, reject) => {
                            const check = () => {
                                const element = document.querySelector(selector);
                                if (element) {
                                    resolve(element);
                                } else if (Date.now() - start >= timeout) {
                                    resolve(null);
                                } else {
                                    requestAnimationFrame(check);
                                }
                            };
                            check();
                        });
                    };
                    
                    // Wait for main content
                    return waitForElement('h1', 10000).then(h1Element => {
                        if (!h1Element) {
                            console.log('Could not find h1 element');
                            return null;
                        }
                        
                        // Get all text content from the page
                        const allText = document.body.innerText;
                        
                        // Find description paragraphs
                        const descriptionParagraphs = Array.from(document.querySelectorAll('p, [class*="description"], [class*="about"]'))
                            .filter(el => {
                                const text = el.innerText.trim();
                                return text.length > 50 && !text.includes('€') && !text.includes('cookie');
                            })
                            .map(el => cleanText(el.innerText));
                        
                        // Find skills
                        const skillElements = document.querySelectorAll('[class*="skill"], [class*="tag"], [class*="competence"]');
                        const rawSkills = Array.from(skillElements)
                            .map(el => cleanText(el.innerText))
                            .filter(text => {
                                return text && 
                                       text.length < 50 && 
                                       !text.includes('NOUVEAU') &&
                                       !text.includes('Autres compétences') &&
                                       !text.includes('Compétences clés') &&
                                       !text.includes('Compétences');
                            });
                            
                        // Split skills that are concatenated with spaces or commas
                        const splitSkills = rawSkills.flatMap(skill => 
                            skill.split(/[,\\s]+/).map(s => s.trim()).filter(s => s.length > 1)
                        );
                        
                        // Normalize and deduplicate skills
                        const normalizedSkills = [...new Set(splitSkills.map(normalizeSkill))].filter(Boolean);
                        
                        // Find experience items
                        const expElements = document.querySelectorAll('[class*="experience"], [class*="parcours"]');
                        const experienceMap = new Map();
                        
                        Array.from(expElements).forEach(exp => {
                            const titleEl = exp.querySelector('h3, h4, [class*="title"]');
                            const companyEl = exp.querySelector('[class*="company"], [class*="entreprise"]');
                            const periodEl = exp.querySelector('[class*="period"], [class*="date"]');
                            const descEl = exp.querySelector('[class*="description"], [class*="content"]');
                            
                            if (titleEl || companyEl || periodEl || descEl) {
                                const title = titleEl ? cleanText(titleEl.innerText) : '';
                                const company = companyEl ? cleanText(companyEl.innerText) : '';
                                const period = periodEl ? cleanText(periodEl.innerText) : '';
                                const description = descEl ? cleanText(descEl.innerText) : '';
                                
                                // Create a unique key for the experience
                                const key = `${title}|${company}|${period}`;
                                
                                // Only add if we don't already have this experience or if this one has more information
                                if (!experienceMap.has(key) || 
                                    description.length > experienceMap.get(key).description.length) {
                                    experienceMap.set(key, {
                                        title,
                                        company,
                                        period,
                                        description
                                    });
                                }
                            }
                        });
                        
                        const experience = Array.from(experienceMap.values())
                            .filter(exp => exp.title || exp.company || exp.period || exp.description)
                            .filter(exp => exp.title !== exp.company || exp.description !== exp.company);
                        
                        // Find location
                        const locationPattern = /(?:Télétravail|Remote|Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Nantes|Strasbourg|Nice)(?:,\\s*France)?/g;
                        const locationMatches = allText.match(locationPattern) || [];
                        const location = [...new Set(locationMatches)].join(', ');
                        
                        // Find rate/tarif
                        const ratePattern = /(\\d+(?:\\s*[€k]|\\s*euros?|\\s*EUR)(?:\\s*\\/\\s*(?:jour|day|j|mois|month|m)))/gi;
                        const rateMatches = allText.match(ratePattern) || [];
                        const rate = rateMatches[0] || '';
                        
                        // Find languages
                        const languagePattern = /(?:Français|French|Anglais|English|Espagnol|Spanish|Allemand|German|Italien|Italian|Arabe|Arabic)(?:\\s*:\\s*(?:Courant|Natif|Bilingue|Intermédiaire|Débutant|Native|Fluent|Intermediate|Beginner))?/gi;
                        const languageMatches = allText.match(languagePattern) || [];
                        const languages = [...new Set(languageMatches)];
                        
                        // Process education
                        const educationMap = new Map();
                        const eduElements = document.querySelectorAll('[class*="education"], [class*="formation"]');
                        
                        Array.from(eduElements).forEach(edu => {
                            const degree = cleanText(getTextContent(edu, '[class*="degree"], [class*="diplome"]'));
                            const school = cleanText(getTextContent(edu, '[class*="school"], [class*="etablissement"]'));
                            const year = cleanText(getTextContent(edu, '[class*="year"], [class*="annee"]'));
                            
                            if (degree || school || year) {
                                const key = `${degree}|${school}|${year}`;
                                if (!educationMap.has(key)) {
                                    educationMap.set(key, { degree, school, year });
                                }
                            }
                        });
                        
                        const education = Array.from(educationMap.values())
                            .filter(edu => edu.degree || edu.school || edu.year);
                        
                        return {
                            title: cleanText(h1Element.innerText),
                            subtitle: document.querySelector('h2') ? cleanText(document.querySelector('h2').innerText) : '',
                            description: descriptionParagraphs.join('\\n'),
                            skills: normalizedSkills,
                            experience,
                            location,
                            rate,
                            availability: document.querySelector('[class*="availability"], [class*="disponibilite"]') ? 
                                        cleanText(document.querySelector('[class*="availability"], [class*="disponibilite"]').innerText) : '',
                            languages,
                            education
                        };
                    });
                """
                
                print("Extracting content using JavaScript...")
                data = self.driver.execute_script(js_script)
                
                # Take screenshot after content extraction
                self.take_screenshot("after_extraction")
                
                return data
                
            except Exception as e:
                print(f"\nError occurred: {str(e)}")
                # Take screenshot on error
                self.take_screenshot("error_page")
                return {'error': str(e)}
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            # Take screenshot on error
            self.take_screenshot("error_page")
            return {'error': str(e)}
            
        finally:
            if hasattr(self, 'driver'):
                print("\nClosing browser...")
                self.driver.quit()

if __name__ == '__main__':
    scraper = MaltScraper(headless=False)
    url = 'https://malt.fr/profile/yacinebenkhedimallah'
    result = scraper.extract_profile_data(url)
    print("\nFinal Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False))