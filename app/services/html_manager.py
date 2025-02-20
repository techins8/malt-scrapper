import os
from datetime import datetime
from typing import Optional
from app.core.config import Config

class HTMLManager:
    def __init__(self, driver, profile_id: str):
        self.driver = driver
        self.profile_id = profile_id
        self.profile_dir = self._get_profile_dir()
        self._ensure_dirs()
    
    def _get_profile_dir(self) -> str:
        """Get the profile directory path"""
        return Config.PROFILE_DIR_TEMPLATE.format(
            base_dir=Config.BASE_DIR,
            profile_id=self.profile_id
        )
    
    def _ensure_dirs(self):
        """Create profile directory if it doesn't exist"""
        os.makedirs(self.profile_dir, exist_ok=True)
    
    def save_page_source(self) -> Optional[str]:
        """Save the current page source as HTML"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = Config.HTML_FILE_TEMPLATE.format(
                base_dir=Config.BASE_DIR,
                profile_id=self.profile_id,
                timestamp=timestamp
            )
            
            # Ensure the directory exists (in case it was deleted)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Get page source and save it
            html_content = self.driver.page_source
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML saved as: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving HTML: {str(e)}")
            return None
