"""API models for request and response data."""
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for HTML translation."""
    
    html: str = Field(..., description="Raw HTML string to translate")
    target_lang: str = Field(..., description="BCP-47 language code (e.g. fr, es-419)")
    source_lang: str | None = Field(
        None, description="Optional source language code"
    )
    batch_size: int = Field(
        100, description="Maximum number of text chunks to translate in one batch"
    )


class TranslationResponse(BaseModel):
    """Response model for HTML translation."""
    
    html: str = Field(..., description="Translated HTML") 