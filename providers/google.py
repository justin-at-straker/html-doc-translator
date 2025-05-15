"""Google Cloud Translation provider implementation."""
import logging
from functools import lru_cache
from typing import List, Tuple

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import translate_v3 as translate

from config import get_settings
from providers.base import TranslationProvider
from services.exceptions import TranslationAPIError

logger = logging.getLogger(__name__)

class GoogleTranslationProvider(TranslationProvider):
    """Google Cloud Translation API provider."""
    
    def __init__(self):
        """Initialize the Google Translation provider."""
        self.client, self.parent = self._get_client_and_parent()
    
    @lru_cache(maxsize=1)
    def _get_client_and_parent(self) -> Tuple[translate.TranslationServiceClient, str]:
        """Get Google Translation client and project parent string."""
        settings = get_settings()
        
        if not settings.gcp_project_id:
            # This RuntimeError will be caught by FastAPI and converted to a 500 error.
            # Proper error handling in the calling code (service/API layer) is expected for user-facing messages.
            logger.error("GCP_PROJECT_ID env var not set. GoogleTranslationProvider cannot be initialized.")
            raise RuntimeError("GCP_PROJECT_ID env var not set")
            
        client = translate.TranslationServiceClient()
        parent = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}"
        return client, parent
    
    def translate_batch(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Translate a batch of strings using Google Cloud Translation API."""
        try:
            resp = self.client.translate_text(
                parent=self.parent,
                contents=texts,
                mime_type="text/plain",
                target_language_code=target_lang,
                source_language_code=source_lang or "",
            )
            return [t.translated_text for t in resp.translations]
        except GoogleAPICallError as e:
            logger.exception(f"Google Cloud Translation API error: {e.message}")
            raise TranslationAPIError(provider_name="Google Cloud", original_exception=e, detail=e.message) from e 