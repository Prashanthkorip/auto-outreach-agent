from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import pickle
import os
from typing import List, Optional
from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_AUTH_URI,
    GOOGLE_TOKEN_URI,
    GOOGLE_REDIRECT_URI,
    SENDER_EMAIL,
)


class EmailSender:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail API."""
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "web": {
                            "client_id": GOOGLE_CLIENT_ID,
                            "client_secret": GOOGLE_CLIENT_SECRET,
                            "auth_uri": GOOGLE_AUTH_URI,
                            "token_uri": GOOGLE_TOKEN_URI,
                            "redirect_uris": [GOOGLE_REDIRECT_URI],
                            "scopes": self.SCOPES,
                        }
                    },
                    self.SCOPES,
                )
                self.creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("gmail", "v1", credentials=self.creds)

    def create_message(self, to: str, subject: str, message_text: str) -> dict:
        """Create a message for an email."""
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = SENDER_EMAIL
        message["subject"] = subject
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
                self.authenticate()

            message = self.create_message(to, subject, message_text)
            self.service.users().messages().send(userId="me", body=message).execute()
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
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
            # Extract name from email (assuming format: name@domain.com)
            name = email.split("@")[0].replace(".", " ").title()

            # Replace placeholder with actual name
            personalized_message = template.replace("Hello", f"Hello {name}")

            if self.send_email(email, subject, personalized_message):
                stats["successful"] += 1
            else:
                stats["failed"] += 1

        return stats
