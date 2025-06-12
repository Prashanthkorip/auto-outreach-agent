import os
from dotenv import load_dotenv

from src.utils.path_finder import PathHelper
import json

# Load environment variables
load_dotenv()

PATH_HELPER = PathHelper()
PATH_HELPER.initialize_resources()


# OpenAI Configuration

openai_api_config = PATH_HELPER.OPENAI_API_JSON
with open(openai_api_config, "r") as f:
    config_data = json.load(f)

OPENAI_API_KEY = config_data.get("OPENAI_API_KEY", "")
OPENAI_MODEL = config_data.get("OPENAI_MODEL", "gpt-4o-mini")


# File paths
RESUME_PATH = "resume_parsed.txt"
RESUME_PDF_PATH = os.path.join(
    PATH_HELPER.WORKING, "SoumithReddyPodduturi.pdf"
)  # Absolute path to resume PDF
DATASET_PATH = PATH_HELPER.RECIPIENT_EMAILS
TEMPLATE_PATH = PATH_HELPER.EMAIL_TEMPLATE
