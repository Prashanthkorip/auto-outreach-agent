import pandas as pd
from job_scraper import JobScraper
from email_generator import EmailGenerator
from email_sender import EmailSender
from config import RESUME_PATH, DATASET_PATH, TEMPLATE_PATH
import os

def load_email_dataset(file_path: str) -> list:
    """Load email addresses from dataset file."""
    try:
        df = pd.read_csv(file_path)
        return df['email'].tolist()  # Assuming the column name is 'email'
    except Exception as e:
        print(f"Error loading email dataset: {str(e)}")
        return []

def load_template(file_path: str) -> str:
    """Load email template from file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading template: {str(e)}")
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
        print("The following required files are missing:")
        for file in missing_files:
            print(f"- {file}")
        print("\nPlease create these files and try again.")
        return
    
    # Initialize components
    job_scraper = JobScraper()
    email_generator = EmailGenerator()
    email_sender = EmailSender()

    # Get job description URL from user
    job_url = input("Please enter the job description URL: ")
    
    # Scrape job page content
    print("Scraping job page content...")
    job_page_text = job_scraper.scrape_job_description(job_url)
    if not job_page_text:
        print("Failed to scrape job page content. Exiting...")
        return
    
    print("Job page content successfully scraped!")
    print("\nExtracted page content (first 5000 characters):")
    print("-" * 50)
    print(job_page_text[:7000] + "..." if len(job_page_text) > 7000 else job_page_text)
    print("-" * 50)
    
    # Confirm with user
    proceed = input("\nDo you want to proceed with this job page content? (y/n): ")
    if proceed.lower() != 'y':
        print("Operation cancelled by user.")
        return

    # Load email template
    print("\nLoading email template...")
    template = load_template(TEMPLATE_PATH)
    if not template:
        print("Failed to load email template. Exiting...")
        return

    # Extract resume text
    print("Extracting resume text...")
    resume_text = email_generator.extract_resume_text(RESUME_PATH)
    if not resume_text:
        print("Failed to extract resume text. Exiting...")
        return

    # Generate email content (extract job description and generate email in one LLM call)
    print("Generating email content...")
    email_content = email_generator.generate_email(template, job_page_text, resume_text, job_url)
    if not email_content:
        print("Failed to generate email content. Exiting...")
        return
    
    print("\nGenerated email content:")
    print("-" * 50)
    print(email_content[:500] + "..." if len(email_content) > 500 else email_content)
    print("-" * 50)
    
    # Confirm with user
    proceed = input("\nDo you want to proceed with sending this email? (y/n): ")
    if proceed.lower() != 'y':
        print("Operation cancelled by user.")
        return

    # Load recipient emails
    print("\nLoading recipient emails...")
    recipients = load_email_dataset(DATASET_PATH)
    if not recipients:
        print("No recipients found in dataset. Exiting...")
        return
    
    print(f"Found {len(recipients)} recipients in the dataset.")

    # Get email subject
    subject = input("\nPlease enter the email subject: ")

    # Send emails
    print("\nSending emails...")
    stats = email_sender.send_bulk_emails(recipients, subject, email_content)

    # Print results
    print("\nEmail sending completed!")
    print(f"Total emails: {stats['total']}")
    print(f"Successfully sent: {stats['successful']}")
    print(f"Failed to send: {stats['failed']}")

if __name__ == "__main__":
    main() 