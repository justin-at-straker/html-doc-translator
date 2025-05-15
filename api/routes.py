"""API routes for the HTML translation service."""
import tempfile
import os
import logging # Import logging
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse # Import FileResponse
from starlette.background import BackgroundTask # For cleanup

from api.models import TranslationResponse # Keep for structure, though not direct response model here
from config import Settings, get_settings
from services.html_translator import translate_html, get_html_from_upload_file
# Import custom service exceptions to catch them
from services.exceptions import FileDecodingError, EmptyFileError, FileProcessingError

# Create router for translation endpoints
router = APIRouter(tags=["translation"])

# Get a logger for this module
logger = logging.getLogger(__name__)

def cleanup_temp_file(file_path: str):
    """Function to remove a temporary file."""
    try:
        os.remove(file_path)
        logger.info(f"Cleaned up temporary file: {file_path}") # Use logger
    except OSError as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {e}") # Use logger


# The response_model is removed here because FileResponse is a direct response type,
# not a Pydantic model that FastAPI would use for validation/serialization in the same way.
# OpenAPI documentation will reflect that it returns a file (typically application/octet-stream or text/html).
@router.post("/translate") # Removed response_model=TranslationResponse
async def translate_endpoint( # Ensure this is async def
    html_file: UploadFile = File(..., description="HTML file to translate"),
    target_lang: str = Form(..., description="BCP-47 language code (e.g. fr, es-419)"),
    source_lang: str | None = Form(None, description="Optional source language code"),
    batch_size: int = Form(100, description="Maximum number of text chunks to translate in one batch"),
    settings: Settings = Depends(get_settings)
) -> FileResponse: # Return type is now FileResponse
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

        # Create a temporary file to store the translated HTML
        # Suffix is .html to help browsers, and delete=False because FileResponse needs to read it.
        # We will clean it up with a BackgroundTask.
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".html") as tmp_file:
            tmp_file.write(translated_html_str)
            temp_file_path = tmp_file.name
        
        # Determine a filename for the downloaded file
        original_filename = html_file.filename or "translated_document.html"
        download_filename = f"translated_{original_filename}"
        
        # Prepare background task for cleanup
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
        logger.error(f"File processing error in /translate: {e}") # Use logger
        raise HTTPException(status_code=422, detail=f"Error processing uploaded file: {str(e)}") from e
    except HTTPException:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise
    except Exception as e:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        logger.exception(f"Unexpected error in /translate endpoint: {e}") # Use logger.exception for unexpected errors to include traceback
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during translation: {str(e)}"
        ) from e
    # Note: The `finally` block for cleanup is now handled by BackgroundTask or explicit calls in error handlers.


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"} 