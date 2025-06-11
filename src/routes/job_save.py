from fastapi import APIRouter, Request
import os
from src.core.config import PATH_HELPER
from src.generation.job_scraper import JobScraper

router = APIRouter()


@router.post("/scrape-job")
async def scrape_job(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "Missing 'url' in request body"}
    job_scraper = JobScraper()
    job_page_text = job_scraper.scrape_job_description(url)
    if not job_page_text:
        return {"error": "Failed to scrape job page content. Exiting..."}
    job_desc_path = os.path.join(PATH_HELPER.WORKING, "JOB_DESCRIPTION.txt")
    with open(job_desc_path, "w", encoding="utf-8") as f:
        f.write(job_page_text)
    return {"description": job_page_text}


@router.post("/save-job-url")
async def save_job_url(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "Missing 'url' in request body"}
    with open(PATH_HELPER.JOB_URL, "w", encoding="utf-8") as f:
        f.write(url)
    return {"message": "Job description saved successfully", "url": url}


@router.post("/save-job-description")
async def save_job_description(request: Request):
    data = await request.json()
    description = data.get("description")
    if not description:
        return {"error": "Missing 'description' in request body"}
    with open(PATH_HELPER.JOB_DESCRIPTION, "w", encoding="utf-8") as f:
        f.write(description)
    return {"message": "Job description saved successfully", "description": description}


@router.get("/get-job-description")
async def get_job_description():
    if not os.path.isfile(PATH_HELPER.JOB_DESCRIPTION):
        return {"description": ""}
    with open(PATH_HELPER.JOB_DESCRIPTION, "r", encoding="utf-8") as f:
        description = f.read()
    return {"description": description}
