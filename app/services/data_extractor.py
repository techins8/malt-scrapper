from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app.core.interfaces import IDataExtractor
from app.core.exceptions import DataExtractionError
from app.core.config import Config
from app.utils.utils import random_sleep
from app.services.html_manager import HTMLManager

class MaltDataExtractor(IDataExtractor):
    def __init__(self, driver, screenshot_manager, cookie_handler):
        self.driver = driver
        self.screenshot_manager = screenshot_manager
        self.cookie_handler = cookie_handler
        self.html_manager = HTMLManager(driver, screenshot_manager.profile_id)
    
    def _check_cloudflare(self):
        """Check and wait for Cloudflare challenge if present"""
        for selector in Config.CLOUDFLARE_SELECTORS:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    print("Detected Cloudflare challenge, waiting for it to complete...")
                    random_sleep(Config.CLOUDFLARE_MIN_SLEEP, Config.CLOUDFLARE_MAX_SLEEP)
                    return True
            except TimeoutException:
                continue
        return False
    
    def extract_profile_data(self, url: str) -> dict:
        try:
            # Navigate to URL
            print(f"Navigating to {url}...")
            self.driver.get(url)
            random_sleep(3, 6)
            
            # Take initial screenshot
            self.screenshot_manager.take_screenshot("initial_page")
            
            # Handle cookie consent
            print("\nHandling cookie consent...")
            self.cookie_handler.handle_cookie_consent()
            
            # Print debug information
            print("\nPage Information:")
            print("Title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            
            # Check for Cloudflare
            self._check_cloudflare()
            
            # Wait for Vue.js to finish rendering
            print("Waiting for Vue.js to finish rendering...")
            random_sleep(10, 15)
            
            # Save the HTML content
            print("Saving page HTML...")
            self.html_manager.save_page_source()
            
            # Execute JavaScript to extract data
            data = self.driver.execute_script(self._get_extraction_script())
            
            return data
            
        except Exception as e:
            raise DataExtractionError(f"Error extracting profile data: {str(e)}")
    
    def _get_extraction_script(self) -> str:
        """Get the JavaScript code for data extraction"""
        return """
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
            
            // Get all text content from the page
            const allText = document.body.innerText;
            const profile = {};
            
            // Basic information
            profile.name = cleanText(document.querySelector('h1')?.innerText || '');
            
            // Extract title from page title
            const pageTitle = document.title;
            const titleMatch = pageTitle.match(/,\s*([^,]+)/);
            profile.title = titleMatch ? cleanText(titleMatch[1].trim()) : '';
            
            // Find description paragraphs
            profile.description = Array.from(document.querySelectorAll('p, [class*="description"], [class*="about"]'))
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
            profile.skills = [...new Set(splitSkills.map(normalizeSkill))].filter(Boolean);
            
            // Extract experiences
            const experienceItems = Array.from(document.querySelectorAll('.profile-experiences-item, .profile-experience, [class*="experience-item"], [class*="mission-item"], [class*="parcours"]'));
            profile.experiences = [];
            
            experienceItems.forEach(item => {
                // Try to find company and title first using specific selectors
                const companySelectors = [
                    '[class*="company"]', '[class*="entreprise"]', '[class*="organization"]',
                    '[class*="client"]', '[class*="employer"]', '[class*="workplace"]'
                ];
                
                const titleSelectors = [
                    '[class*="title"]', '[class*="poste"]', '[class*="role"]',
                    '[class*="position"]', '[class*="job"]', '[class*="fonction"]'
                ];
                
                let company = '';
                let title = '';
                let period = '';
                
                // Try to find company using selectors
                for (const selector of companySelectors) {
                    const el = item.querySelector(selector);
                    if (el) {
                        company = el.textContent.trim();
                        break;
                    }
                }
                
                // Try to find title using selectors
                for (const selector of titleSelectors) {
                    const el = item.querySelector(selector);
                    if (el) {
                        title = el.textContent.trim();
                        break;
                    }
                }
                
                // Get all text content for further processing
                const text = item.textContent || '';
                
                // Try to find period with format "month year - month year (duration)"
                const periodRegex = /(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\\s+(\\d{4})\\s*-\\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|présent|aujourd'hui)\\s*(\\d{4})?\\s*(?:\\((.*?)\\))?/i;
                const periodMatch = text.match(periodRegex);
                
                if (periodMatch) {
                    period = periodMatch[0];
                }
                
                // Split text into lines and clean them
                const lines = text.split(/\\n/)
                    .map(l => l.trim())
                    .filter(l => l && l.length > 2)  // Remove empty lines and very short ones
                    .filter(l => !l.match(/^[\\s\\-–—]*$/)) // Remove separator lines
                    .filter(l => !l.match(/^\\s*\\d+\\s*$/)); // Remove lines with just numbers
                
                // If we haven't found company/title through selectors, try to parse from text
                if (!company || !title) {
                    // First non-empty line usually contains important information
                    const firstLine = lines[0];
                    
                    // Common patterns for job titles
                    const titlePatterns = [
                        'consultant', 'chef de projet', 'lead', 'manager', 
                        'développeur', 'ingénieur', 'architecte', 'expert',
                        'analyst', 'specialist'
                    ];
                    
                    const hasTitle = firstLine && titlePatterns.some(pattern => 
                        firstLine.toLowerCase().includes(pattern)
                    );
                    
                    if (!title && hasTitle) {
                        title = firstLine;
                    } else if (!company) {
                        company = firstLine;
                        
                        // Try to find title in second line if we found company in first
                        if (lines.length > 1) {
                            const secondLine = lines[1];
                            const hasTitle = secondLine && titlePatterns.some(pattern => 
                                secondLine.toLowerCase().includes(pattern)
                            );
                            if (!title && hasTitle) {
                                title = secondLine;
                            }
                        }
                    }
                }
                
                // Clean up company/title if they contain each other
                if (company && title) {
                    if (company && company.toLowerCase && title && title.toLowerCase && company.toLowerCase().includes(title.toLowerCase())) {
                        company = company.replace(new RegExp(title, 'i'), '').trim();
                    }
                    if (title && title.toLowerCase && company && company.toLowerCase && title.toLowerCase().includes(company.toLowerCase())) {
                        title = title.replace(new RegExp(company, 'i'), '').trim();
                    }
                }
                
                // Get description (everything after company/title/period)
                const descriptionStart = Math.max(
                    lines.indexOf(company) + 1,
                    lines.indexOf(title) + 1,
                    lines.findIndex(l => l.includes(period)) + 1,
                    0  // Fallback if none found
                );
                
                const description = lines
                    .slice(descriptionStart)
                    .filter(line => 
                        !line.includes(period) &&     // Remove lines containing the period
                        line !== company &&           // Remove lines that are exactly company or title
                        line !== title &&
                        !line.match(/^(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)/i)  // Remove lines starting with months
                    )
                    .join('\\n');
                
                // Only add if we have meaningful data
                if ((company || title) && (period || description)) {
                    // Clean up company/title if they contain each other
                    if (company && title) {
                        if (company.toLowerCase && title.toLowerCase && company.toLowerCase().includes(title.toLowerCase())) {
                            company = company.replace(new RegExp(title, 'i'), '').trim();
                        }
                        if (title.toLowerCase && company.toLowerCase && title.toLowerCase().includes(company.toLowerCase())) {
                            title = title.replace(new RegExp(company, 'i'), '').trim();
                        }
                    }
                    
                    // Final validation
                    if (company || title) {
                        profile.experiences.push({
                            company: company || 'Non spécifié',
                            title: title || 'Non spécifié',
                            period,
                            description
                        });
                    }
                }
            });
            
            // Remove duplicates and sort by period (most recent first)
            profile.experiences = profile.experiences
                .filter((exp, index, self) => 
                    index === self.findIndex(e => 
                        e.company === exp.company && 
                        e.title === exp.title && 
                        e.period === exp.period
                    )
                )
                .sort((a, b) => {
                    const yearA = a.period.match(/\\d{4}/);
                    const yearB = b.period.match(/\\d{4}/);
                    return (yearB ? parseInt(yearB[0]) : 0) - (yearA ? parseInt(yearA[0]) : 0);
                });
            
            // Find location
            const locationPattern = /(?:Télétravail|Remote|Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Nantes|Strasbourg|Nice)(?:,\\s*France)?/g;
            const locationMatches = allText.match(locationPattern) || [];
            profile.location = [...new Set(locationMatches)].join(', ');
            
            // Find rate/tarif
            const ratePattern = /(\\d+(?:\\s*[€k]|\\s*euros?|\\s*EUR)(?:\\s*\\/\\s*(?:jour|day|j|mois|month|m)))/gi;
            const rateMatches = allText.match(ratePattern) || [];
            profile.rate = rateMatches[0] || '';
            
            // Find languages
            const languagePattern = /(?:Français|French|Anglais|English|Espagnol|Spanish|Allemand|German|Italien|Italian|Arabe|Arabic)(?:\\s*:\\s*(?:Courant|Natif|Bilingue|Intermédiaire|Débutant|Native|Fluent|Intermediate|Beginner))?/gi;
            const languageMatches = allText.match(languagePattern) || [];
            profile.languages = [...new Set(languageMatches)];
            
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
            
            profile.education = Array.from(educationMap.values())
                .filter(edu => edu.degree || edu.school || edu.year);
            
            return profile;
        """
