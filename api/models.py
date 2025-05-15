"""API models for request and response data."""
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for HTML translation.
    
    Represents the data structure for translation parameters, 
    though not directly used as body for form-based /translate endpoint.
    """
    
    html: str = Field(..., description="Raw HTML string to translate (used if not file upload)")
    target_lang: str = Field(..., description="BCP-47 language code (e.g. fr, es-419)")
    source_lang: str | None = Field(
        None, description="Optional source language code"
    )
    batch_size: int = Field(
        100, description="Maximum number of text chunks to translate in one batch"
    )


class TranslationResponse(BaseModel):
    """Response model for HTML translation if returning JSON.
    
    Note: The /translate endpoint currently returns a FileResponse directly.
    This model would be used if an endpoint returned translated HTML in a JSON payload.
    """
    html: str = Field(..., description="Translated HTML") 