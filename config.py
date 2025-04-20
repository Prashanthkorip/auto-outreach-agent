import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# File paths
RESUME_PATH = "resume_parsed.txt"
DATASET_PATH = "email_dataset.csv"
TEMPLATE_PATH = "email_template.txt"
