"""API routes for the HTML translation service."""
import tempfile
import os
import logging
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from services.html_translator import translate_html, get_html_from_upload_file
from services.exceptions import (
    FileDecodingError, EmptyFileError, FileProcessingError, 
    TranslationAPIError, InsufficientQuotaError, TranslationError
)
from providers import get_available_provider_names
from typing import List

router = APIRouter(tags=["translation"])
logger = logging.getLogger(__name__)

def cleanup_temp_file(file_path: str):
    """Function to remove a temporary file."""
    try:
        os.remove(file_path)
        logger.info(f"Cleaned up temporary file: {file_path}")
    except OSError as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {e}")

@router.post("/translate")
async def translate_endpoint(
    html_file: UploadFile = File(..., description="HTML file to translate"),
    target_lang: str = Form(..., description="BCP-47 language code (e.g. fr, es-419)"),
    source_lang: str | None = Form(None, description="Optional source language code"),
    batch_size: int = Form(100, description="Maximum number of text chunks to translate in one batch"),
) -> FileResponse:
    """Translate an uploaded HTML file and return it as a downloadable file.
    
    Accepts multipart/form-data and returns the translated HTML file.
    """
    temp_file_path = None
    try:
        html_content_str = await get_html_from_upload_file(html_file)

        translated_html_str = await translate_html(
            html=html_content_str,
            target_lang=target_lang,
            source_lang=source_lang,
            batch_size=batch_size,
        )

        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".html") as tmp_file:
            tmp_file.write(translated_html_str)
            temp_file_path = tmp_file.name
        
        original_filename = html_file.filename or "translated_document.html"
        download_filename = f"translated_{original_filename}"
        
        cleanup_task = BackgroundTask(cleanup_temp_file, temp_file_path)

        return FileResponse(
            path=temp_file_path,
            media_type='text/html',
            filename=download_filename,
            background=cleanup_task
        )

    except FileDecodingError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except EmptyFileError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileProcessingError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.error(f"File processing error in /translate: {e}")
        raise HTTPException(status_code=422, detail=f"Error processing uploaded file: {str(e)}") from e
    except InsufficientQuotaError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.warning(f"Translation failed due to insufficient quota: {e}")
        raise HTTPException(status_code=429, detail=str(e)) from e
    except TranslationAPIError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.error(f"Translation API error in /translate: {e}")
        raise HTTPException(status_code=502, detail=f"Translation service provider error: {str(e)}") from e
    except TranslationError as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.error(f"Generic translation error in /translate: {e}")
        raise HTTPException(status_code=500, detail=f"Error during translation process: {str(e)}") from e
    except HTTPException:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise
    except Exception as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.exception(f"Unexpected error in /translate endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during translation: {str(e)}"
        ) from e

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@router.get("/providers", response_model=List[str])
async def list_translation_providers():
    """Lists the available translation provider names."""
    try:
        provider_names = get_available_provider_names()
        return provider_names
    except Exception as e:
        logger.exception("Error fetching available provider names.")
        raise HTTPException(
            status_code=500, 
            detail="Could not retrieve list of available providers."
        ) from e 