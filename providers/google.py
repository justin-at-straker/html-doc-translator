"""Google Cloud Translation provider implementation."""
from functools import lru_cache
from typing import List, Tuple

from fastapi import HTTPException
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import translate_v3 as translate

from config import get_settings
from providers.base import TranslationProvider


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
            raise HTTPException(502, f"Translation API error: {e.message}") from e 