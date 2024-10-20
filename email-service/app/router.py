from fastapi import APIRouter

from .emails.endpoints import router as emails_router

router = APIRouter()

router.include_router(emails_router, prefix="/emails", tags=["emails"])
