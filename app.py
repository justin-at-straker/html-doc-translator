"""
HTML Translation Microservice
============================

A FastAPI microservice that translates HTML content while preserving structure,
with support for multiple translation providers.

Environment Variables:
    GCP_PROJECT_ID: Your Google Cloud project ID (required for Google provider)
    GCP_LOCATION: Translation API location (default: global)
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON key
    TRANSLATION_PROVIDER: Which translation provider to use (default: google)

Usage:
    pip install -r requirements.txt
    uvicorn app:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from logging_config import setup_logging # Import the setup function

# Initialize logging
setup_logging() 

# Create FastAPI application
app = FastAPI(
    title="HTML Translation Service",
    description="Translate HTML content while preserving structure",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "HTML Translation Service",
        "version": "1.0.0",
        "docs_url": "/docs",
    } 