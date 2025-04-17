import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_AUTH_URI = os.getenv('GOOGLE_AUTH_URI')
GOOGLE_TOKEN_URI = os.getenv('GOOGLE_TOKEN_URI')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

# File paths
RESUME_PATH = '/Users/spartan/Documents/projects/coldmail-automation/prashanth.txt'
DATASET_PATH = '/Users/spartan/Documents/projects/coldmail-automation/email_dataset.csv'
TEMPLATE_PATH = '/Users/spartan/Documents/projects/coldmail-automation/email_template.txt'

# Email Configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL') 