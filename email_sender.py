import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from logger import logger


class EmailSender:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        self.creds = None
        self.service = None
        self.pdf_path = "ai.pdf"  # PDF file path

    def authenticate(self):
        """Authenticate with Gmail API using credentials.json file."""
        try:
            # Check if token.json exists and load credentials from it
            if os.path.exists("token.json"):
                logger.info("Loading existing credentials from token.json")
                self.creds = Credentials.from_authorized_user_file(
                    "token.json", self.SCOPES
                )

            # If credentials are not valid, refresh or create new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    try:
                        self.creds.refresh(Request())
                    except Exception as e:
                        logger.error(f"Error refreshing credentials: {str(e)}")
                        self.creds = None
                        if os.path.exists("token.json"):
                            os.remove("token.json")

                # If still no valid credentials, create new ones
                if not self.creds:
                    logger.info(
                        "Starting new authentication flow using credentials.json"
                    )
                    if not os.path.exists("credentials.json"):
                        raise FileNotFoundError(
                            "credentials.json file not found. Please download it from Google Cloud Console."
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", self.SCOPES
                    )
                    self.creds = flow.run_local_server(
                        port=0,
                        success_message="Authentication successful! You can close this window.",
                        open_browser=True,
                    )

                # Save the credentials for future use
                logger.info("Saving credentials to token.json")
                with open("token.json", "w") as token:
                    token.write(self.creds.to_json())

            # Build the Gmail service
            logger.info("Building Gmail service")
            self.service = build("gmail", "v1", credentials=self.creds)
            logger.info("Gmail service built successfully")

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.service = None
            raise

    def create_message(self, to: str, subject: str, message_text: str) -> dict:
        """Create a message for an email."""
        # Convert markdown-style links to HTML links
        message_text = re.sub(
            r"\[(.*?)\]\((.*?)\)",
            r'<a href="\2" style="color: #0366d6; text-decoration: none;">\1</a>',
            message_text,
        )

        # Convert plain URLs to clickable links (if any remain)
        url_pattern = r'(?<!href=")(https?://\S+)(?!")'
        message_text = re.sub(
            url_pattern,
            r'<a href="\1" style="color: #0366d6; text-decoration: none;">\1</a>',
            message_text,
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 15px;
                    max-width: 100%;
                    color: #24292e;
                }}
                p {{
                    margin-bottom: 1em;
                    word-wrap: break-word;
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                @media screen and (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            {message_text.replace("\n\n", "</p><p>").replace("\n", "<br>")}
        </body>
        </html>
        """

        # Create the root message as multipart
        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject

        # Add HTML body
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Add PDF attachment if it exists
        if os.path.exists(self.pdf_path):
            with open(self.pdf_path, "rb") as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(self.pdf_path),
                )
                message.attach(pdf_attachment)

        return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, to: str, subject: str, message_text: str) -> bool:
        """
        Send an email using Gmail API.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            message_text (str): Email body

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if not self.service:
                logger.info("Gmail service not initialized, authenticating...")
                self.authenticate()
                if not self.service:
                    logger.error("Failed to initialize Gmail service")
                    return False

            logger.info(f"Sending email to {to}")
            logger.info(f"Subject: {subject}")
            logger.debug(
                f"Message: {message_text}"
            )  # Changed to debug level for long messages

            message = self.create_message(to, subject, message_text)
            if not message:
                logger.error("Failed to create email message")
                return False

            self.service.users().messages().send(userId="me", body=message).execute()
            logger.info(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def send_bulk_emails(
        self, recipients: List[str], subject: str, template: str
    ) -> dict:
        """
        Send emails to multiple recipients.

        Args:
            recipients (List[str]): List of recipient email addresses
            subject (str): Email subject
            template (str): Email template with placeholder for name

        Returns:
            dict: Statistics about sent emails
        """
        stats = {"total": len(recipients), "successful": 0, "failed": 0}

        for email in recipients:
            try:
                if not email or not isinstance(email, str):
                    logger.warning(f"Skipping invalid email address: {email}")
                    stats["failed"] += 1
                    continue

                # Extract name from email (assuming format: name@domain.com)
                name = email.split("@")[0].replace(".", " ").title()
                if not name:
                    logger.warning(f"Could not extract name from email: {email}")
                    name = "there"  # Fallback to a generic greeting

                # Replace placeholder with actual name
                personalized_message = template.replace("Hello", f"Hello {name}")

                if self.send_email(email, subject, personalized_message):
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1
            except Exception as e:
                logger.error(f"Error processing email {email}: {str(e)}")
                stats["failed"] += 1

        return stats
