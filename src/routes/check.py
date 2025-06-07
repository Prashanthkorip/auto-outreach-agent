import os
from fastapi import APIRouter

from src.core.config import PATH_HELPER

router = APIRouter()


# Health and file check endpoints will be included here
@router.get("/file-check")
def env_check():
    """Health check endpoint."""
    missing = []

    # Check OPENAI_API_KEY.txt
    openai_key_path = PATH_HELPER.OPENAI_API_JSON
    if not os.path.isfile(openai_key_path):
        missing.append("OPENAI_API_KEY")
    else:
        with open(openai_key_path, "r") as f:
            key = f.read().strip()
            if not key:
                missing.append("OPENAI_API_KEY")

    # Check credentials.json
    credentials_path = PATH_HELPER.get_credentials_file()
    if not os.path.isfile(credentials_path):
        missing.append("credentials.json")

    if missing:
        return {"missing": missing}
    return {"message": "success"}
