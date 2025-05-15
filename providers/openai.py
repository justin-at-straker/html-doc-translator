"""OpenAI Translation provider implementation."""
import asyncio
from typing import List
import logging
from openai import AsyncOpenAI, APIStatusError

from config import get_settings
from providers.base import TranslationProvider
from services.exceptions import TranslationAPIError, InsufficientQuotaError, TranslationError

logger = logging.getLogger(__name__)

class OpenAITranslationProvider(TranslationProvider):
    """OpenAI API provider for translations."""

    def __init__(self):
        """Initialize the OpenAI Translation provider."""
        settings = get_settings()
        if not settings.openai_api_key:
            logger.error("OPENAI_API_KEY env var not set. OpenAITranslationProvider cannot be initialized.")
            raise RuntimeError("OPENAI_API_KEY env var not set")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def _translate_single_text(self, text: str, target_lang: str, source_lang: str | None) -> str:
        """Helper to translate a single text string using OpenAI."""
        prompt = f"Translate the following text from {source_lang or 'autodetect'} to {target_lang}:\n\n{text}\n\nTranslated text:"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful translation assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=len(text.split()) * 2 + 50
            )
            translated_text = response.choices[0].message.content.strip()
            return translated_text
        except APIStatusError as e:
            logger.exception(f"OpenAI API status error: {e}")
            if e.status_code == 429:
                raise InsufficientQuotaError(provider_name="OpenAI", original_exception=e) from e
            raise TranslationAPIError(provider_name="OpenAI", original_exception=e, detail=str(e)) from e
        except Exception as e:
            logger.exception(f"OpenAI API error during single text translation: {e}")
            # Generic catch for other OpenAI client errors or unexpected issues
            raise TranslationAPIError(provider_name="OpenAI", original_exception=e, detail=str(e)) from e

    def translate_batch(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Translate a batch of strings using OpenAI API via synchronous wrapper.
        
        This method is a synchronous wrapper around the async implementation.
        It's provided for compatibility with the base class's synchronous signature but is not recommended 
        if the calling context is already asynchronous, as it will block the event loop.
        Prefer using `translate_batch_async` if possible.
        """
        logger.warning(
            "Synchronous `translate_batch` called on OpenAITranslationProvider. "
            "This will block the event loop. Prefer `translate_batch_async`."
        )
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # This is a fallback for when called from FastAPI's sync execution path.
                # It's not ideal and can lead to issues. A proper async call stack is preferred.
                logger.warning("OpenAI's translate_batch running new event loop from a running one. This is highly unperformant.")
                # This approach of creating a new task and running it to completion from a sync method
                # inside an async framework is tricky and often discouraged.
                # It might be better to use `asyncio.run_coroutine_threadsafe` if interacting with a different thread's loop,
                # or restructure the calling code to be fully async.
                # Given the context, we will attempt to run it, but this signals a design smell.
                # A simple `return asyncio.run(self.translate_batch_async(texts, target_lang, source_lang))`
                # would fail if called from within an already running event loop (like FastAPI does for sync endpoints).
                # Fallback: run in new thread to avoid RuntimeError: asyncio.run() cannot be called from a running event loop.
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.translate_batch_async(texts, target_lang, source_lang))
                    return future.result()
            else:
                return asyncio.run(self.translate_batch_async(texts, target_lang, source_lang))
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                 logger.error(
                    "asyncio.run() failed within OpenAITranslationProvider.translate_batch. " 
                    "This indicates a sync call from an async environment. Refactor to use translate_batch_async."
                 )
                 # As a last resort, if truly stuck in a sync context that itself is in an async framework
                 # this might be an indication that `starlette.concurrency.run_in_threadpool` should have been used
                 # by the caller of this sync method.
                 # Raising the original error as this situation is complex and context-dependent.
            raise TranslationError(f"Failed to execute OpenAI batch synchronously: {e}") from e

    async def translate_batch_async(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Asynchronously translate a batch of strings using OpenAI API."""
        tasks = [self._translate_single_text(text, target_lang, source_lang) for text in texts]
        try:
            translations = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = []
            for i, res in enumerate(translations):
                if isinstance(res, Exception):
                    logger.error(f"Error translating text item {i}: {texts[i]} with OpenAI -> {res}")
                    # This exception 'res' could be one of our custom ones if it failed in _translate_single_text
                    if isinstance(res, TranslationError):
                        raise res # Re-raise if it's already one of our specific types
                    # Otherwise, wrap it
                    raise TranslationAPIError(provider_name="OpenAI", original_exception=res, detail=f"Error translating item: {texts[i]}") from res
                results.append(res)
            return results
            
        except Exception as e:
            logger.exception(f"OpenAI batch translation error: {e}")
            if isinstance(e, TranslationError): # Re-raise if already a custom translation error
                raise
            raise TranslationAPIError(provider_name="OpenAI", original_exception=e) from e 