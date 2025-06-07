from fastapi import APIRouter, Request, HTTPException, UploadFile, File
import os
import json
from json import JSONDecodeError
from src.core.config import PATH_HELPER
from src.generation.job_scraper import JobScraper
from src.utils.logger import logger
from src.utils.read_resume import PDFExtractor

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    with open(PATH_HELPER.RESUME_PDF, "wb") as f:
        content = await file.read()
        f.write(content)
    pdf = PDFExtractor()
    text = pdf.extract_text(PATH_HELPER.RESUME_PDF)
    with open(PATH_HELPER.RESUME_EXTRACT, "w", encoding="utf-8") as f:
        f.write(text)
    return {"description": text}


@router.get("/get-resume-description")
async def get_resume_description():
    if not os.path.isfile(PATH_HELPER.RESUME_EXTRACT):
        return {"description": ""}
    with open(PATH_HELPER.RESUME_EXTRACT, "r", encoding="utf-8") as f:
        description = f.read()
    return {"description": description}


@router.post("/save-resume-description")
async def save_resume_description(request: Request):
    data = await request.json()
    description = data.get("description")
    if not description:
        return {"description": ""}
    with open(PATH_HELPER.RESUME_EXTRACT, "w", encoding="utf-8") as f:
        f.write(description)
    return {"description": description}
