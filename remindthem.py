#!/usr/bin/env python3
"""
Follow-up Email Reminder Script

This script reads the email tracking data and sends follow-up emails 
to recipients who were contacted at least 2 days ago and haven't 
received a follow-up yet.
"""

import datetime
from typing import List, Dict
import time

from email_sender import EmailSender
from email_tracker import EmailTracker
from logger import logger


class FollowUpManager:
    """Manages follow-up email campaigns."""
    
    def __init__(self, tracking_file: str = "email_tracking.xlsx"):
        """
        Initialize the follow-up manager.
        
        Args:
            tracking_file: Path to the email tracking Excel file
        """
        self.email_sender = EmailSender(tracking_file)
        self.tracker = EmailTracker(tracking_file)
        
    def generate_followup_content(self, first_name: str, original_subject: str, company_name: str = "the company") -> tuple:
        """
        Generate follow-up email content and subject.
        
        Args:
            first_name: Recipient's first name
            original_subject: Original email subject (for threading)
            company_name: Company name (extracted from subject or default)
            
        Returns:
            Tuple of (subject, content)
        """
        # Use original subject for proper threading - the email sender will add "Re: " prefix
        subject = original_subject
        
        content = f"""Hi {first_name},

I hope you're well!

Just following up on my previous email about the **ML Intern roles** at {company_name}. I'm very excited about the possibility of contributing to the team.

If there's anything further you need, please let me know!

Thanks again, I look forward to your reply.

Best,
**Prashanth Koripalli**"""
        
        return subject, content
    
    def extract_company_from_subject(self, subject: str) -> str:
        """
        Extract company name from email subject.
        
        Args:
            subject: Original email subject
            
        Returns:
            Company name or default
        """
        try:
            # Look for common patterns in subject lines
            if " at " in subject:
                parts = subject.split(" at ")
                if len(parts) > 1:
                    company = parts[-1].strip()
                    # Clean up the company name
                    company = company.replace("!", "").replace("?", "").strip()
                    return company
            
            # Fallback patterns
            for keyword in ["intern", "position", "role", "opportunity"]:
                if keyword in subject.lower():
                    words = subject.split()
                    for i, word in enumerate(words):
                        if keyword.lower() in word.lower() and i > 0:
                            potential_company = words[i-1]
                            if len(potential_company) > 2:
                                return potential_company
            
            return "the company"
            
        except Exception as e:
            logger.warning(f"Error extracting company from subject '{subject}': {str(e)}")
            return "the company"
    
    def send_followup_emails(self, days_threshold: int = 2, delay_seconds: int = 5) -> Dict:
        """
        Send follow-up emails to contacts who need them.
        
        Args:
            days_threshold: Number of days to wait before sending follow-up
            delay_seconds: Delay between sending emails to avoid rate limits
            
        Returns:
            Statistics about sent follow-ups
        """
        try:
            # Get emails that need follow-up
            emails_needing_followup = self.tracker.get_emails_needing_followup(days_threshold)
            
            if not emails_needing_followup:
                logger.info("No emails need follow-up at this time.")
                return {"total": 0, "successful": 0, "failed": 0}
            
            logger.info(f"Found {len(emails_needing_followup)} emails that need follow-up")
            
            stats = {"total": len(emails_needing_followup), "successful": 0, "failed": 0}
            
            for i, email_record in enumerate(emails_needing_followup, 1):
                try:
                    email_address = email_record["email"]
                    first_name = email_record["first_name"]
                    original_subject = email_record["subject"]
                    original_timestamp = email_record["timestamp"]
                    original_message_id = email_record.get("message_id", "")
                    
                    # Extract company name from original subject
                    company_name = self.extract_company_from_subject(original_subject)
                    
                    # Generate follow-up content
                    followup_subject, followup_content = self.generate_followup_content(
                        first_name, original_subject, company_name
                    )
                    
                    logger.info(f"Sending follow-up {i}/{len(emails_needing_followup)} to {email_address}")
                    if original_message_id:
                        logger.info(f"Threading as reply to message: {original_message_id}")
                    
                    # Send follow-up email as reply to original
                    result = self.email_sender.send_email(
                        email_address, 
                        followup_subject, 
                        followup_content,
                        is_followup=True,
                        reply_to_message_id=original_message_id if original_message_id else None
                    )
                    
                    if result["success"]:
                        stats["successful"] += 1
                        # Mark the original email as having received a follow-up
                        self.tracker.mark_followup_sent(email_address, original_timestamp)
                        logger.info(f"✅ Follow-up sent successfully to {email_address}")
                    else:
                        stats["failed"] += 1
                        logger.error(f"❌ Failed to send follow-up to {email_address}")
                    
                    # Add delay between emails to avoid rate limits
                    if i < len(emails_needing_followup):
                        logger.info(f"Waiting {delay_seconds} seconds before next email...")
                        time.sleep(delay_seconds)
                        
                except Exception as e:
                    logger.error(f"Error processing follow-up for {email_record.get('email', 'unknown')}: {str(e)}")
                    stats["failed"] += 1
            
            # Export updated tracking data
            self.tracker.export_to_excel()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in send_followup_emails: {str(e)}")
            return {"total": 0, "successful": 0, "failed": 0}
    
    def preview_followups(self, days_threshold: int = 2) -> None:
        """
        Preview emails that would receive follow-ups without sending them.
        
        Args:
            days_threshold: Number of days to wait before sending follow-up
        """
        try:
            emails_needing_followup = self.tracker.get_emails_needing_followup(days_threshold)
            
            if not emails_needing_followup:
                logger.info("No emails need follow-up at this time.")
                return
            
            logger.info(f"\n📧 FOLLOW-UP PREVIEW ({len(emails_needing_followup)} emails)")
            logger.info("=" * 60)
            
            for i, record in enumerate(emails_needing_followup, 1):
                email_address = record["email"]
                first_name = record["first_name"]
                original_subject = record["subject"]
                sent_date = record["date"]
                company_name = self.extract_company_from_subject(original_subject)
                
                logger.info(f"{i}. {email_address} ({first_name})")
                logger.info(f"   Original: {original_subject}")
                logger.info(f"   Sent: {sent_date}")
                logger.info(f"   Company: {company_name}")
                logger.info("")
                
        except Exception as e:
            logger.error(f"Error in preview_followups: {str(e)}")


def main():
    """Main function to run the follow-up email script."""
    try:
        logger.info("🚀 Starting Follow-up Email Manager")
        
        # Initialize the follow-up manager
        followup_manager = FollowUpManager()
        
        # Preview what emails would get follow-ups
        logger.info("\n📋 PREVIEW MODE")
        followup_manager.preview_followups(days_threshold=2)
        
        # Ask user for confirmation
        proceed = input("\nDo you want to send these follow-up emails? (y/n): ").strip().lower()
        
        if proceed in ['y', 'yes']:
            logger.info("\n📤 SENDING FOLLOW-UP EMAILS")
            stats = followup_manager.send_followup_emails(days_threshold=2, delay_seconds=5)
            
            # Print results
            logger.info("\n✅ FOLLOW-UP CAMPAIGN COMPLETED!")
            logger.info(f"Total emails processed: {stats['total']}")
            logger.info(f"Successfully sent: {stats['successful']}")
            logger.info(f"Failed to send: {stats['failed']}")
            
            if stats['total'] > 0:
                success_rate = (stats['successful'] / stats['total']) * 100
                logger.info(f"Success rate: {success_rate:.1f}%")
                logger.info(f"\n📊 Updated tracking data saved to email_tracking.xlsx")
        else:
            logger.info("❌ Follow-up campaign cancelled by user.")
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Follow-up campaign interrupted by user.")
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")


if __name__ == "__main__":
    main() 