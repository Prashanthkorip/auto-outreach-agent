from fastapi import APIRouter, Request
import os
from src.core.config import PATH_HELPER
from fastapi import Body

from src.generation.email_generator import EmailGenerator

router = APIRouter()


@router.post("/generate-email")
async def generate_email():

    with open(PATH_HELPER.JOB_URL, "r") as f:
        job_url = f.read().strip()

    with open(PATH_HELPER.JOB_DESCRIPTION, "r") as f:
        job_page_text = f.read().strip()
        job_page_text = (
            job_page_text[:7000] + "..." if len(job_page_text) > 7000 else job_page_text
        )

    with open(PATH_HELPER.EMAIL_TEMPLATE, "r") as f:
        email_template = f.read()

    with open(PATH_HELPER.RESUME_EXTRACT, "r") as f:
        resume_parsed_text = f.read()

    email_generator = EmailGenerator()
    email_content, email_subject = email_generator.generate_email(
        email_template, job_page_text, resume_parsed_text, job_url
    )

    with open(PATH_HELPER.EMAIL_GENERATED, "w") as f:
        f.write(f"{email_subject}\n\n{email_content}")

    if not email_content or not email_subject:
        return {"error": "Failed to generate email content or subject. Exiting..."}
    return {"subject": email_subject, "content": email_content}


@router.get("/get-generated-email")
async def get_generated_email():
    try:
        with open(PATH_HELPER.EMAIL_GENERATED, "r") as f:
            content = f.read()
        if "\n\n" in content:
            subject, body = content.split("\n\n", 1)
        else:
            subject, body = "", content
        return {"subject": subject, "content": body}
    except FileNotFoundError:
        return {"error": "Generated email not found."}


@router.post("/save-generated-email")
async def save_generated_email(request: Request):
    data = await request.json()
    email_subject = data.get("subject")
    email_content = data.get("content")
    with open(PATH_HELPER.EMAIL_GENERATED, "w") as f:
        f.write(f"{email_subject}\n\n{email_content}")
    return {"subject": email_subject, "content": email_content}
