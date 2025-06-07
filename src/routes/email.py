from fastapi import APIRouter, Request
import os
from src.core.config import PATH_HELPER

router = APIRouter()


@router.get("/get-email-template")
async def get_email_template():
    if not os.path.isfile(PATH_HELPER.EMAIL_TEMPLATE):
        return {"error": "Email template not found"}
    with open(PATH_HELPER.EMAIL_TEMPLATE, "r", encoding="utf-8") as f:
        description = f.read()
    return {"description": description}


@router.post("/save-email-template")
async def save_email_template(request: Request):
    data = await request.json()
    description = data.get("description")
    if not description:
        return {"description": ""}
    with open(PATH_HELPER.EMAIL_TEMPLATE, "w", encoding="utf-8") as f:
        f.write(description)
    return {
        "description": description,
    }
