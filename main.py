import pandas as pd
from job_scraper import JobScraper
from email_generator import EmailGenerator
from email_sender import EmailSender
from config import RESUME_PATH, DATASET_PATH, TEMPLATE_PATH
import os
from logger import logger


def load_email_dataset(file_path: str) -> list:
    """Load email addresses from dataset file."""
    try:
        df = pd.read_csv(file_path)
        return df["email"].tolist()  # Assuming the column name is 'email'
    except Exception as e:
        logger.error(f"Error loading email dataset: {str(e)}")
        return []


def load_template(file_path: str) -> str:
    """Load email template from file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        return ""


def check_files_exist():
    """Check if all required files exist."""
    missing_files = []

    if not os.path.exists(RESUME_PATH):
        missing_files.append(f"Resume file: {RESUME_PATH}")

    if not os.path.exists(DATASET_PATH):
        missing_files.append(f"Email dataset: {DATASET_PATH}")

    if not os.path.exists(TEMPLATE_PATH):
        missing_files.append(f"Email template: {TEMPLATE_PATH}")

    return missing_files


def main():
    # Check if all required files exist
    missing_files = check_files_exist()
    if missing_files:
        logger.error("The following required files are missing:")
        for file in missing_files:
            logger.error(f"- {file}")
        logger.error("\nPlease create these files and try again.")
        return

    # Initialize components
    job_scraper = JobScraper()
    email_generator = EmailGenerator()
    email_sender = EmailSender()

    # Get job description URL from user
    job_url = input("Please enter the job description URL: ")

    # Scrape job page content
    logger.info("Scraping job page content...")
    job_page_text = job_scraper.scrape_job_description(job_url)
    if not job_page_text:
        logger.error("Failed to scrape job page content. Exiting...")
        return

    logger.info("Job page content successfully scraped!")
    logger.info("\nExtracted page content (first 5000 characters):")
    logger.info("-" * 50)
    logger.info(
        job_page_text[:7000] + "..." if len(job_page_text) > 7000 else job_page_text
    )
    logger.info("-" * 50)

    # Confirm with user
    proceed = input("\nDo you want to proceed with this job page content? (y/n): ")
    if proceed.lower() not in ["y", "yes"]:
        logger.info("Operation cancelled by user.")
        return

    # Load email template
    logger.info("\nLoading email template...")
    template = load_template(TEMPLATE_PATH)
    if not template:
        logger.error("Failed to load email template. Exiting...")
        return

    # Extract resume text
    logger.info("Extracting resume text...")
    resume_text = email_generator.extract_resume_text(RESUME_PATH)
    if not resume_text:
        logger.error("Failed to extract resume text. Exiting...")
        return

    # Generate email content (extract job description and generate email in one LLM call)
    logger.info("Generating email content...")
    email_content = email_generator.generate_email(
        template, job_page_text, resume_text, job_url
    )
    if not email_content:
        logger.error("Failed to generate email content. Exiting...")
        return

    logger.info("\nGenerated email content:")
    logger.info("-" * 50)
    logger.info(
        email_content[:500] + "..." if len(email_content) > 500 else email_content
    )
    logger.info("-" * 50)

    # Confirm with user
    proceed = input("\nDo you want to proceed with sending this email? (y/n): ")
    if proceed.lower() != "y":
        logger.info("Operation cancelled by user.")
        return

    # Load recipient emails
    logger.info("\nLoading recipient emails...")
    recipients = load_email_dataset(DATASET_PATH)
    if not recipients:
        logger.error("No recipients found in dataset. Exiting...")
        return

    logger.info(f"Found {len(recipients)} recipients in the dataset.")

    # Get email subject
    subject = input("\nPlease enter the email subject: ")

    # Send emails
    logger.info("\nSending emails...")
    stats = email_sender.send_bulk_emails(recipients, subject, email_content)

    # Print results
    logger.info("\nEmail sending completed!")
    logger.info(f"Total emails: {stats['total']}")
    logger.info(f"Successfully sent: {stats['successful']}")
    logger.info(f"Failed to send: {stats['failed']}")


if __name__ == "__main__":
    main()
