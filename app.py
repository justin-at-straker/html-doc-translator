from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="HTML Translation Service",
    description="Translate HTML content while preserving structure",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "HTML Translation Service",
        "version": "1.0.0",
        "docs_url": "/docs",
    } 