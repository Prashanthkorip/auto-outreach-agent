from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import os
import random
from typing import Optional, List, Dict
from logger import logger
from fake_useragent import UserAgent
import undetected_chromedriver as uc


class BrowserProfile:
    """Manages browser profile and anti-detection measures."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.viewport_sizes = [
            (1920, 1080),
            (1366, 768),
            (1440, 900),
            (1536, 864)
        ]
        
    def get_random_viewport(self) -> tuple:
        """Get random viewport size."""
        return random.choice(self.viewport_sizes)
        
    def get_random_user_agent(self) -> str:
        """Get random user agent."""
        return self.ua.random
        
    def get_random_delay(self, min_delay: float = 2.0, max_delay: float = 5.0) -> float:
        """Get random delay between actions."""
        return random.uniform(min_delay, max_delay)


class LinkedInEmailScraper:
    def __init__(self, apollo_extension_path: str):
        """
        Initialize the LinkedIn email scraper.
        
        Args:
            apollo_extension_path: Path to the Apollo.io Chrome extension
        """
        self.apollo_extension_path = apollo_extension_path
        self.driver = None
        self.browser_profile = BrowserProfile()
        self.session_count = 0
        self.max_profiles_per_session = 20  # Maximum profiles to scrape per session

    def _setup_chrome(self) -> None:
        """Set up Chrome with Apollo.io extension and anti-detection measures."""
        try:
            # Use undetected-chromedriver for better anti-detection
            options = uc.ChromeOptions()
            
            # Add Apollo.io extension
            options.add_extension(self.apollo_extension_path)
            
            # Random viewport size
            width, height = self.browser_profile.get_random_viewport()
            options.add_argument(f"--window-size={width},{height}")
            
            # Random user agent
            options.add_argument(f"--user-agent={self.browser_profile.get_random_user_agent()}")
            
            # Additional anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-save-password-bubble")
            options.add_argument("--disable-translate")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            # Add random proxy if available
            if os.getenv("PROXY_LIST"):
                proxy = random.choice(os.getenv("PROXY_LIST").split(","))
                options.add_argument(f"--proxy-server={proxy}")
            
            # Initialize the driver
            self.driver = uc.Chrome(options=options)
            
            # Set window size
            self.driver.set_window_size(width, height)
            
            # Add random mouse movements
            self._add_random_mouse_movements()
            
        except Exception as e:
            logger.error(f"Error setting up Chrome: {str(e)}")
            raise

    def _add_random_mouse_movements(self) -> None:
        """Add random mouse movements to appear more human-like."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            
            # Get window size
            window_size = self.driver.get_window_size()
            width, height = window_size['width'], window_size['height']
            
            # Perform random movements
            for _ in range(3):
                x = random.randint(0, width)
                y = random.randint(0, height)
                actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.warning(f"Error adding mouse movements: {str(e)}")

    def _human_like_scroll(self) -> None:
        """Perform human-like scrolling behavior."""
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_step = random.randint(100, 300)
            
            while current_position < total_height:
                current_position += scroll_step
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {str(e)}")

    def _should_rotate_session(self) -> bool:
        """Check if we should rotate the session."""
        self.session_count += 1
        return self.session_count >= self.max_profiles_per_session

    def _rotate_session(self) -> None:
        """Rotate the session by closing and reopening the browser."""
        if self.driver:
            self.driver.quit()
        self.session_count = 0
        time.sleep(random.uniform(30, 60))  # Wait between sessions
        self._setup_chrome()

    def login_to_linkedin(self, email: str, password: str) -> bool:
        """
        Log in to LinkedIn with human-like behavior.
        
        Args:
            email: LinkedIn login email
            password: LinkedIn password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Add random delay before typing
            time.sleep(self.browser_profile.get_random_delay(1.0, 2.0))
            
            # Wait for and fill in email with human-like typing
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            for char in email:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Add random delay between fields
            time.sleep(self.browser_profile.get_random_delay(0.5, 1.0))
            
            # Fill in password with human-like typing
            password_field = self.driver.find_element(By.ID, "password")
            for char in password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Add random delay before clicking
            time.sleep(self.browser_profile.get_random_delay(0.5, 1.0))
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete with random delay
            time.sleep(self.browser_profile.get_random_delay(3.0, 5.0))
            
            return "feed" in self.driver.current_url
            
        except Exception as e:
            logger.error(f"Error logging into LinkedIn: {str(e)}")
            return False

    def wait_for_apollo_extension(self, timeout: int = 10) -> bool:
        """Wait for Apollo.io extension to load."""
        try:
            # Wait for Apollo extension iframe or button
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-apollo-widget]"))
            )
            return True
        except TimeoutException:
            return False

    def extract_email_from_profile(self, profile_url: str) -> Optional[str]:
        """
        Extract email from a LinkedIn profile using Apollo.io extension.
        
        Args:
            profile_url: URL of the LinkedIn profile
            
        Returns:
            Optional[str]: Extracted email if found, None otherwise
        """
        try:
            # Navigate to profile
            self.driver.get(profile_url)
            
            # Add random delay after page load
            time.sleep(self.browser_profile.get_random_delay(2.0, 4.0))
            
            # Perform human-like scrolling
            self._human_like_scroll()
            
            # Wait for Apollo extension
            if not self.wait_for_apollo_extension():
                logger.warning(f"Apollo extension not loaded for {profile_url}")
                return None
            
            # Add random delay before clicking
            time.sleep(self.browser_profile.get_random_delay(1.0, 2.0))
            
            # Click Apollo button to reveal email
            apollo_button = self.driver.find_element(By.CSS_SELECTOR, "[data-apollo-widget]")
            apollo_button.click()
            
            # Wait for email to load with random delay
            time.sleep(self.browser_profile.get_random_delay(1.5, 3.0))
            
            # Extract email from Apollo widget
            email_element = self.driver.find_element(By.CSS_SELECTOR, ".apollo-email-field")
            email = email_element.text
            
            return email if "@" in email else None
            
        except Exception as e:
            logger.error(f"Error extracting email from {profile_url}: {str(e)}")
            return None

    def process_profile_list(self, profile_urls: List[str]) -> Dict[str, str]:
        """
        Process a list of LinkedIn profiles and extract emails.
        
        Args:
            profile_urls: List of LinkedIn profile URLs
            
        Returns:
            Dict[str, str]: Dictionary mapping profile URLs to emails
        """
        results = {}
        
        try:
            self._setup_chrome()
            
            for url in profile_urls:
                # Check if we need to rotate session
                if self._should_rotate_session():
                    self._rotate_session()
                    if not self.login_to_linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD")):
                        logger.error("Failed to login after session rotation")
                        break
                
                email = self.extract_email_from_profile(url)
                results[url] = email
                
                # Add random delay between profiles
                time.sleep(self.browser_profile.get_random_delay(5.0, 10.0))
                
        except Exception as e:
            logger.error(f"Error processing profiles: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                
        return results

    def save_results(self, results: Dict[str, str], output_file: str) -> None:
        """Save results to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}") 