from linkedin_scraper import LinkedInEmailScraper
from typing import List
import json
import os
from logger import logger


def load_profile_urls(input_file: str) -> List[str]:
    """Load LinkedIn profile URLs from a file."""
    try:
        with open(input_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error loading profile URLs: {str(e)}")
        return []


def main():
    # Configuration
    APOLLO_EXTENSION_PATH = "path/to/apollo.crx"  # Replace with actual path
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    INPUT_FILE = "linkedin_profiles.txt"
    OUTPUT_FILE = "extracted_emails.json"

    # Check required environment variables
    if not all([LINKEDIN_EMAIL, LINKEDIN_PASSWORD]):
        logger.error("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        return

    # Load profile URLs
    profile_urls = load_profile_urls(INPUT_FILE)
    if not profile_urls:
        logger.error(f"No profile URLs found in {INPUT_FILE}")
        return

    # Initialize scraper
    scraper = LinkedInEmailScraper(APOLLO_EXTENSION_PATH)

    try:
        # Set up Chrome and login
        scraper._setup_chrome()
        if not scraper.login_to_linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
            logger.error("Failed to login to LinkedIn")
            return

        # Process profiles
        results = scraper.process_profile_list(profile_urls)

        # Save results
        scraper.save_results(results, OUTPUT_FILE)

        # Print summary
        total = len(profile_urls)
        found = sum(1 for email in results.values() if email)
        logger.info(f"Processing complete: Found {found} emails out of {total} profiles")

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
    finally:
        if scraper.driver:
            scraper.driver.quit()


if __name__ == "__main__":
    main() 