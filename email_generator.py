from typing import Optional

import openai

from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger


class EmailGenerator:
    def __init__(self):
        # Initialize the OpenAI client with the API key
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    def extract_resume_text(self, resume_path: str) -> Optional[str]:
        """
        Extract text from resume text file.

        Args:
            resume_path (str): Path to the resume text file

        Returns:
            Optional[str]: Extracted text from resume or None if extraction fails
        """
        try:
            with open(resume_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting resume text: {str(e)}")
            return None

    def generate_email(
        self, template: str, job_page_text: str, resume_text: str, job_url: str
    ) -> Optional[str]:
        """
        Generate personalized email using LLM in a single call.
        This function extracts the job description from the page text and generates the email.

        Args:
            template (str): Email template
            job_page_text (str): Raw text from the job posting page
            resume_text (str): Extracted resume text
            job_url (str): URL of the job posting

        Returns:
            Optional[str]: Generated email or None if generation fails
        """
        try:
            # Truncate text if it's too long for the API
            max_text_length = 12000  # Adjust based on model's token limit
            if len(job_page_text) > max_text_length:
                job_page_text = job_page_text[:max_text_length] + "..."
                logger.warning(
                    f"Job page text was truncated to {max_text_length} characters"
                )

            prompt = f"""
            I need you to perform two tasks:
            
            1. First, extract the job description from this webpage content:
            
            {job_page_text}
            
            Please identify and extract:
            - Job title
            - Company name (if available)
            - Job responsibilities
            - Required qualifications
            - Preferred qualifications (if any)
            - Any other relevant details about the position
            
            2. Then, using the extracted job description, generate a personalized email using this template:
            
            {template}
            
            And this resume:
            
            {resume_text}
            
            Please generate a professional email that:
            1. Follows the template structure
            2. Highlights relevant experience from the resume that matches the job description
            3. Includes a personalized greeting (use "Hello" as placeholder)
            4. Ends with the job description link: {job_url}
            5. Maintains a professional and engaging tone
            
            Format your response as a complete email ready to be sent.
            """

            # Use the client instance to make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer helping to create personalized job application emails.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            return None
