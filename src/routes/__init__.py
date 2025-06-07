from fastapi import APIRouter
from .check import router as check_router
from .resume import router as resume_router
from .job import router as job_router
from .email import router as email_router
from .openai import router as openai_router
from .credentials import router as credentials_router
from .recipient import router as recipient_router
from .generate import router as generate_router
from .send_mail import router as send_mail_router

router = APIRouter()

router.include_router(check_router)
router.include_router(resume_router)
router.include_router(job_router)
router.include_router(email_router)
router.include_router(openai_router)
router.include_router(credentials_router)
router.include_router(recipient_router)
router.include_router(generate_router)
router.include_router(send_mail_router)
