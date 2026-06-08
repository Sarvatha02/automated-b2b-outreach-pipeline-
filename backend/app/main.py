"""
Automated Outreach Pipeline - FastAPI Backend
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import pipeline, results, emails, export
from app.config.settings import settings
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Automated Outreach Pipeline API")
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Automated Outreach Pipeline",
    description="Discover companies, find decision-makers, resolve emails, and send personalized outreach.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])


@app.get("/")
async def root():
    return {"message": "Automated Outreach Pipeline API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
