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

from src.utils.logger import logger
from src.core.config import PATH_HELPER, RESUME_PDF_PATH
from src.tracking.email_tracker import EmailTracker


class EmailSender:
    def __init__(self, tracking_file: str = "email_tracking.xlsx"):
        self.SCOPES = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
        ]
        self.creds = None
        self.service = None
        self.pdf_path = RESUME_PDF_PATH  # Use the resume PDF path from config
        self.tracker = EmailTracker(tracking_file)  # Initialize tracker

    def authenticate(self):
        """Authenticate with Gmail API using credentials.json file."""
        try:
            # Check if token.json exists and load credentials from it
            if os.path.exists(PATH_HELPER.TOKEN_JSON):
                logger.info("Loading existing credentials from token.json")
                self.creds = Credentials.from_authorized_user_file(
                    PATH_HELPER.TOKEN_JSON, self.SCOPES
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
                        if os.path.exists(PATH_HELPER.TOKEN_JSON):
                            os.remove(PATH_HELPER.TOKEN_JSON)

                # If still no valid credentials, create new ones
                if not self.creds:
                    logger.info(
                        "Starting new authentication flow using credentials.json"
                    )
                    if not os.path.exists(PATH_HELPER.CREDENTIALS_JSON):
                        raise FileNotFoundError(
                            "credentials.json file not found. Please download it from Google Cloud Console."
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        PATH_HELPER.CREDENTIALS_JSON, self.SCOPES
                    )
                    self.creds = flow.run_local_server(
                        port=0,
                        success_message="Authentication successful! You can close this window.",
                        open_browser=True,
                    )

                # Save the credentials for future use
                logger.info("Saving credentials to token.json")
                with open(PATH_HELPER.TOKEN_JSON, "w") as token:
                    token.write(self.creds.to_json())

            # Build the Gmail service
            logger.info("Building Gmail service")
            self.service = build("gmail", "v1", credentials=self.creds)
            logger.info("Gmail service built successfully")

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.service = None
            raise

    def get_message_headers(self, message_id: str) -> dict:
        """
        Get headers from an existing message for threading.

        Args:
            message_id: Gmail message ID

        Returns:
            Dict containing relevant headers
        """
        try:
            if not self.service:
                return {}

            message = (
                self.service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=["Message-ID", "Subject"],
                )
                .execute()
            )

            headers = {}
            if "payload" in message and "headers" in message["payload"]:
                for header in message["payload"]["headers"]:
                    if header["name"] == "Message-ID":
                        headers["message_id"] = header["value"]
                    elif header["name"] == "Subject":
                        headers["subject"] = header["value"]

            return headers

        except Exception as e:
            logger.warning(
                f"Could not retrieve message headers for {message_id}: {str(e)}"
            )
            return {}

    def create_message(
        self, to: str, subject: str, message_text: str, reply_to_message_id: str = None
    ) -> dict:
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

        # Convert **text** to bold text
        message_text = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
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
                strong {{
                    font-weight: bold;
                    color: #24292e;
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

        # Handle threading for replies
        if reply_to_message_id:
            # Get the original message headers
            original_headers = self.get_message_headers(reply_to_message_id)
            original_message_id = original_headers.get("message_id", "")
            original_subject = original_headers.get("subject", subject)

            # Set proper reply subject
            if not subject.startswith("Re: ") and not original_subject.startswith(
                "Re: "
            ):
                message["subject"] = f"Re: {original_subject}"
            elif original_subject.startswith("Re: "):
                message["subject"] = original_subject
            else:
                message["subject"] = subject

            # Add threading headers if we have the original Message-ID
            if original_message_id:
                message["In-Reply-To"] = original_message_id
                message["References"] = original_message_id
                logger.info(f"Threading reply with Message-ID: {original_message_id}")
            else:
                logger.warning(f"Could not retrieve original Message-ID for threading")
        else:
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

    def send_email(
        self,
        to: str,
        subject: str,
        message_text: str,
        is_followup: bool = False,
        reply_to_message_id: str = None,
    ) -> dict:
        """
        Send an email using Gmail API.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            message_text (str): Email body
            is_followup (bool): Whether this is a follow-up email
            reply_to_message_id (str): Message ID to reply to (for threading)

        Returns:
            dict: Contains success status and message_id if successful
        """
        try:
            if not self.service:
                logger.info("Gmail service not initialized, authenticating...")
                self.authenticate()
                if not self.service:
                    logger.error("Failed to initialize Gmail service")
                    self.tracker.log_email_attempt(
                        to,
                        subject,
                        "failed",
                        "Failed to initialize Gmail service",
                        is_followup=is_followup,
                    )
                    return {"success": False, "message_id": None}

            logger.info(f"Sending email to {to}")
            logger.info(f"Subject: {subject}")
            if reply_to_message_id:
                logger.info(f"Replying to message ID: {reply_to_message_id}")
            logger.debug(
                f"Message: {message_text}"
            )  # Changed to debug level for long messages

            message = self.create_message(
                to, subject, message_text, reply_to_message_id
            )
            if not message:
                logger.error("Failed to create email message")
                self.tracker.log_email_attempt(
                    to,
                    subject,
                    "failed",
                    "Failed to create email message",
                    is_followup=is_followup,
                )
                return {"success": False, "message_id": None}

            # If this is a follow-up, try to get the thread ID from the original message
            send_params = {"userId": "me", "body": message}
            if reply_to_message_id:
                try:
                    original_message = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=reply_to_message_id, format="minimal")
                        .execute()
                    )

                    if "threadId" in original_message:
                        send_params["body"]["threadId"] = original_message["threadId"]
                        logger.info(f"Using thread ID: {original_message['threadId']}")
                except Exception as e:
                    logger.warning(f"Could not get thread ID: {str(e)}")

            result = self.service.users().messages().send(**send_params).execute()
            message_id = result.get("id")
            logger.info(f"Email sent successfully to {to}, Message ID: {message_id}")
            self.tracker.log_email_attempt(
                to, subject, "success", message_id=message_id, is_followup=is_followup
            )
            return {"success": True, "message_id": message_id}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error sending email: {error_msg}")
            self.tracker.log_email_attempt(
                to, subject, "failed", error_msg, is_followup=is_followup
            )
            return {"success": False, "message_id": None}

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
        stats = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "success": True,
        }

        for name, email in recipients:
            try:
                if not email or not isinstance(email, str):
                    logger.warning(f"Skipping invalid email address: {email}")
                    stats["failed"] += 1
                    self.tracker.log_email_attempt(
                        email, subject, "failed", "Invalid email address"
                    )
                    continue

                # Extract name from email (assuming format: name@domain.com)
                name = name.title()
                if not name:
                    logger.warning(f"Could not extract name from email: {email}")
                    name = "there"  # Fallback to a generic greeting

                # Replace placeholder with actual name
                personalized_message = template.replace("Hello", f"Hello {name}")

                result = self.send_email(email, subject, personalized_message)
                stats["success"] = stats["success"] or result["success"]
                if result["success"]:
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing email {email}: {error_msg}")
                self.tracker.log_email_attempt(
                    email, subject, "failed", f"Processing error: {error_msg}"
                )
                stats["failed"] += 1

        # Export tracking data to Excel after bulk sending
        self.tracker.export_to_excel()

        # Print summary statistics
        tracker_stats = self.tracker.get_statistics()
        logger.info(f"Tracking Summary:")
        logger.info(f"  Total emails processed: {tracker_stats['total']}")
        logger.info(f"  Successful: {tracker_stats['successful']}")
        logger.info(f"  Failed: {tracker_stats['failed']}")
        logger.info(f"  Success rate: {tracker_stats['success_rate']:.1f}%")

        return stats

    def get_tracking_statistics(self) -> dict:
        """Get current tracking statistics."""
        return self.tracker.get_statistics()

    def export_tracking_data(self, filename: str = None) -> None:
        """Export tracking data to Excel."""
        if filename:
            self.tracker.output_file = filename
        self.tracker.export_to_excel()

    def clear_tracking_data(self) -> None:
        """Clear all tracking data."""
        self.tracker.clear_data()
