import logging

from fastapi import FastAPI

from .postgres import postgres
from .router import router


def create_application() -> FastAPI:
    application = FastAPI(openapi_url="/users/openapi.json", docs_url="/users/docs")
    application.include_router(router, prefix="/api/v1", tags=["users"])
    return application


app = create_application()
log = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    postgres.init_database()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
