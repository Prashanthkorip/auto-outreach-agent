import csv
from fastapi import APIRouter, Request
import os
from src.core.config import PATH_HELPER
from fastapi import Body

from src.generation.email_generator import EmailGenerator
from src.utils.email_sender import EmailSender
import datetime
from urllib.parse import urlparse
import shutil

router = APIRouter()


@router.post("/send-email")
async def send_generated_email():
    try:
        with open(PATH_HELPER.EMAIL_GENERATED, "r") as f:
            content = f.read()
        if "\n\n" in content:
            subject, content = content.split("\n\n", 1)
        else:
            subject, content = "", content

        email_sender = EmailSender("email_tracking.xlsx")
        recipients = []
        with open(PATH_HELPER.RECIPIENT_EMAILS, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipients.append((row["name"], row["email"]))
        stats = email_sender.send_bulk_emails(recipients, subject, content)
        if stats["success"]:
            with open(PATH_HELPER.JOB_URL, "r") as f:
                job_url = f.read()
            with open(PATH_HELPER.JOB_DESCRIPTION, "r") as f:
                job_description = f.read()
            with open(PATH_HELPER.RESUME_EXTRACT, "r") as f:
                resume_extract = f.read()
            with open(PATH_HELPER.RECIPIENT_EMAILS, "r") as f:
                recipient_emails = f.read()
            with open(PATH_HELPER.EMAIL_GENERATED, "r") as f:
                email_generated = f.read()

            separator = "\n\n" + "-" * 40 + "\n\n"
            combined_content = (
                "JOB_URL:\n"
                + job_url
                + separator
                + "JOB_DESCRIPTION:\n"
                + job_description
                + separator
                + "RESUME_EXTRACT:\n"
                + resume_extract
                + separator
                + "RECIPIENT_EMAILS:\n"
                + recipient_emails
                + separator
                + "EMAIL_GENERATED:\n"
                + email_generated
            )

            # Extract domain from job_url
            parsed_url = urlparse(job_url.strip())
            domain = parsed_url.netloc.replace(".", "_")

            # Get current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")

            # Create file path
            # Create directories if they don't exist
            applications_dir = PATH_HELPER.APPLICATIONS
            domain_dir = os.path.join(applications_dir, domain)
            date_dir = os.path.join(domain_dir, current_date)
            os.makedirs(date_dir, exist_ok=True)

            # Final file path to save
            file_path = os.path.join(date_dir, "JOB_DETAILS.txt")

            # Write combined_content to the generated file path
            with open(file_path, "w") as f:
                f.write(combined_content)

            resume_pdf_src = PATH_HELPER.RESUME_PDF
            resume_pdf_dst = os.path.join(date_dir, os.path.basename(resume_pdf_src))
            if os.path.exists(resume_pdf_src):
                shutil.move(resume_pdf_src, resume_pdf_dst)

            # Empty the working directory from PATH_HELPER
            for file_path in [
                PATH_HELPER.EMAIL_GENERATED,
                PATH_HELPER.JOB_URL,
                PATH_HELPER.JOB_DESCRIPTION,
                PATH_HELPER.RESUME_EXTRACT,
                PATH_HELPER.RECIPIENT_EMAILS,
                PATH_HELPER.RESUME_PDF,
            ]:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)

        return {
            "sent": stats["total"],
            "successful": stats["successful"],
            "failed": stats["failed"],
        }
    except FileNotFoundError:
        return {"error": "Generated email not found."}
