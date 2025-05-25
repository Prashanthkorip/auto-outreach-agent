import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from logger import logger


class JobScraper:
    def __init__(self):
        # Common User-Agent strings
        self.chrome_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.firefox_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
        
        # Default headers
        self.headers = {
            "User-Agent": self.chrome_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        # Common job description selectors
        self.job_selectors = [
            # Class-based selectors
            "job-description", "jobDescription", "job-details", "jobDetails",
            "description", "job-content", "jobContent", "job-body", "jobBody",
            "position-description", "positionDescription", "role-description",
            "roleDescription", "vacancy-description", "vacancyDescription",
            # ID-based selectors
            "job-description", "jobDescription", "job-details", "jobDetails",
            "description", "job-content", "jobContent", "job-body", "jobBody",
            # Role-based selectors
            "main", "article", "content", "main-content", "mainContent"
        ]

        # Site-specific configurations
        self.site_configs = {
            "metacareers.com": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'job-description')]",
                "custom_headers": {
                    "User-Agent": self.chrome_ua,
                    "Referer": "https://www.metacareers.com/",
                }
            },
            "tesla.com": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'tds-content-block')]",
                "timeout": 30,
                "custom_headers": {
                    "User-Agent": self.chrome_ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                    "TE": "trailers",
                }
            },
            "linkedin.com": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'job-description')]",
                "timeout": 15,
            },
            "indeed.com": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'jobsearch-jobDescriptionText')]",
                "timeout": 15,
            },
            "glassdoor.com": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'jobDescriptionContent')]",
                "timeout": 15,
            },
            "lever.co": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'content')]",
                "timeout": 10,
            },
            "greenhouse.io": {
                "use_selenium": True,
                "wait_for": "//div[contains(@class, 'opening-info')]",
                "timeout": 10,
            },
        }

    def _setup_selenium(self) -> webdriver.Chrome:
        """Set up Chrome in headless mode with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.chrome_ua}")
        chrome_options.add_argument("--window-size=1920,1080")
        # Add these options for better compatibility
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        return webdriver.Chrome(options=chrome_options)

    def _get_site_config(self, url: str) -> dict:
        """Get site-specific configuration based on the URL domain."""
        domain = urlparse(url).netloc.replace("www.", "")
        return self.site_configs.get(domain, {})

    def _find_job_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the job description content using multiple strategies."""
        # Strategy 1: Try common job description selectors
        for selector in self.job_selectors:
            # Try class-based selectors
            content = soup.find("div", {"class": selector})
            if content:
                return content
            
            # Try ID-based selectors
            content = soup.find("div", {"id": selector})
            if content:
                return content

        # Strategy 2: Look for common job-related text
        job_keywords = ["job description", "position description", "role description", 
                       "about the role", "about this role", "about the position"]
        
        for keyword in job_keywords:
            # Find elements containing job-related text
            elements = soup.find_all(["div", "section", "article"], 
                                   string=lambda text: text and keyword.lower() in text.lower())
            if elements:
                # Get the parent or next sibling that likely contains the description
                for element in elements:
                    # Try parent
                    parent = element.parent
                    if parent and len(parent.get_text()) > 100:  # Ensure it's substantial content
                        return parent
                    
                    # Try next sibling
                    next_sibling = element.find_next_sibling()
                    if next_sibling and len(next_sibling.get_text()) > 100:
                        return next_sibling

        # Strategy 3: Find the largest text block that looks like a job description
        text_blocks = soup.find_all(["div", "section", "article"])
        if text_blocks:
            # Filter blocks that look like job descriptions
            job_blocks = [block for block in text_blocks 
                         if len(block.get_text()) > 200 and  # Substantial content
                         any(keyword in block.get_text().lower() 
                             for keyword in ["requirements", "responsibilities", "qualifications"])]
            
            if job_blocks:
                # Return the largest block
                return max(job_blocks, key=lambda x: len(x.get_text()))

        # Strategy 4: Fallback to main content
        return soup.find("main") or soup.find("article") or soup.find("body")

    def _clean_content(self, soup: BeautifulSoup) -> str:
        """Clean and extract relevant content from the page."""
        # Remove unnecessary elements
        for element in soup(["script", "style", "nav", "header", "footer", "iframe", "meta"]):
            element.decompose()

        # Find the job content
        main_content = self._find_job_content(soup)

        if main_content:
            # Extract text with better formatting
            lines = []
            for element in main_content.stripped_strings:
                line = element.strip()
                if line:  # Only add non-empty lines
                    lines.append(line)

            # Join all lines with proper spacing
            return "\n".join(lines)
        
        return soup.get_text(separator="\n", strip=True)

    def _scrape_with_selenium(self, url: str, config: dict) -> Optional[str]:
        """Scrape content using Selenium for JavaScript-heavy sites."""
        try:
            driver = self._setup_selenium()
            
            # Set page load timeout
            driver.set_page_load_timeout(config.get("timeout", 30))
            
            # Add custom headers if specified
            if "custom_headers" in config:
                for key, value in config["custom_headers"].items():
                    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {key: value}})
            
            # Navigate to the URL
            driver.get(url)

            # Wait for specific element if configured
            if "wait_for" in config:
                timeout = config.get("timeout", 10)
                try:
                    element = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, config["wait_for"]))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for element: {config['wait_for']}")
                    # Try alternative selectors for Tesla
                    if "tesla.com" in url:
                        try:
                            element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "tds-content-block"))
                            )
                        except TimeoutException:
                            logger.warning("Timeout waiting for Tesla alternative selector")

            # Give additional time for dynamic content to load
            time.sleep(3)

            # Get the page source after JavaScript execution
            page_source = driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Clean up the content
            return self._clean_content(soup)

        except Exception as e:
            logger.error(f"Error in Selenium scraping: {str(e)}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass

    def scrape_job_description(self, url: str) -> Optional[str]:
        """
        Scrape job description from the given URL using appropriate method.
        
        Args:
            url (str): The URL of the job posting

        Returns:
            Optional[str]: The scraped job description or None if scraping fails
        """
        try:
            # Get site-specific configuration
            config = self._get_site_config(url)

            # Use Selenium for sites that require JavaScript
            if config.get("use_selenium", False):
                logger.info(f"Using Selenium for {url}")
                return self._scrape_with_selenium(url, config)

            # Use requests for simpler sites
            headers = {**self.headers, **config.get("custom_headers", {})}
            response = requests.get(
                url,
                headers=headers,
                timeout=config.get("timeout", 10)
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            return self._clean_content(soup)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping job description: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while scraping: {str(e)}")
            return None


# One issue I already see here is if the header dosent match Job Description title, then it will not be able to scrape the job description.
