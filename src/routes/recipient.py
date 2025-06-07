from fastapi import APIRouter, Request, HTTPException, UploadFile, File
import os
import json
from json import JSONDecodeError
from src.core.config import PATH_HELPER
from src.generation.job_scraper import JobScraper
from src.utils.logger import logger
from src.utils.read_resume import PDFExtractor
import csv

router = APIRouter()


@router.get("/get-recipients")
async def get_resume_description():
    if not os.path.isfile(PATH_HELPER.RECIPIENT_EMAILS):
        return {"recipients": []}
    recipients = []
    with open(PATH_HELPER.RECIPIENT_EMAILS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipients.append(row)
    return {"recipients": recipients}


@router.post("/save-recipients")
async def save_resume_description(request: Request):
    data = await request.json()
    recipients = data.get("recipients", [])
    if not recipients:
        return {"recipients": []}
    fieldnames = ["id", "name", "email"]
    with open(PATH_HELPER.RECIPIENT_EMAILS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        print(f"Saving recipients: {recipients}")
        writer.writeheader()
        for rec in recipients:
            writer.writerow(
                {
                    "id": rec.get("id", ""),
                    "name": rec.get("name", ""),
                    "email": rec.get("email", ""),
                }
            )
    return {"recipients": recipients}
