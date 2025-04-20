import requests
from bs4 import BeautifulSoup
from typing import Optional


class JobScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def scrape_job_description(self, url: str) -> Optional[str]:
        """
        Scrape job description from the given URL.

        Args:
            url (str): The URL of the job posting

        Returns:
            Optional[str]: The scraped job description or None if scraping fails
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unnecessary elements that might contain irrelevant text
            for element in soup(
                ["script", "style", "nav", "header", "footer", "iframe", "meta"]
            ):
                element.extract()

            # Get the main content
            main_content = (
                soup.find("main") or soup.find("article") or soup.find("body")
            )

            if main_content:
                # Extract text with better formatting
                lines = []

                # Get all text elements
                for element in main_content.stripped_strings:
                    line = element.strip()
                    if line:  # Only add non-empty lines
                        lines.append(line)

                # Join all lines with proper spacing
                page_text = "\n".join(lines)

                return page_text
            else:
                # Fallback: get all text from the page
                return soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"Error scraping job description: {str(e)}")
            return None


# One issue I already see here is if the header dosent match Job Description title, then it will not be able to scrape the job description.
