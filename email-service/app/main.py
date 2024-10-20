import logging

from fastapi import FastAPI

from .router import router


def create_application() -> FastAPI:
    application = FastAPI(openapi_url="/email/openapi.json", docs_url="/emails/docs")
    application.include_router(router, prefix="/api/v1", tags=["emails"])
    return application


app = create_application()
log = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
