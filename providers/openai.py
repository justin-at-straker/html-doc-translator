"""OpenAI Translation provider implementation."""
import asyncio
from typing import List
import logging # Import logging
from openai import AsyncOpenAI
from fastapi import HTTPException

from config import get_settings
from providers.base import TranslationProvider

# Get a logger for this module
logger = logging.getLogger(__name__)

class OpenAITranslationProvider(TranslationProvider):
    """OpenAI API provider for translations."""

    def __init__(self):
        """Initialize the OpenAI Translation provider."""
        settings = get_settings()
        if not settings.openai_api_key:
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
                temperature=0.3, # Lower temperature for more deterministic translation
                max_tokens=len(text.split()) * 2 + 50 # Estimate tokens needed
            )
            translated_text = response.choices[0].message.content.strip()
            return translated_text
        except Exception as e:
            # Log the error or handle it more gracefully
            logger.exception(f"OpenAI API error during single text translation: {e}")
            raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")


    def translate_batch(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Translate a batch of strings using OpenAI API.
        
        Note: OpenAI's chat completions are not inherently designed for batch translation
        in the same way some other dedicated translation APIs are. This implementation
        will make concurrent requests for each text item in the batch.
        For very large batches, consider rate limits and alternative strategies.
        """
        
        # FastAPI runs in an event loop, so we can use asyncio.gather for concurrency
        # If this were a synchronous context, we might use threading or other methods.
        async def translate_all():
            tasks = [self._translate_single_text(text, target_lang, source_lang) for text in texts]
            return await asyncio.gather(*tasks)

        try:
            # Attempt to get or create an event loop for this synchronous method
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # If inside a running loop (e.g. FastAPI endpoint), create a task
                # This is a common pattern when calling async code from sync in such frameworks
                # However, Pydantic models and FastAPI itself will usually handle this.
                # Direct call to `asyncio.run` inside a running loop causes errors.
                # For simplicity and since this provider might be used outside FastAPI too,
                # we'll try to run it in a new loop if necessary, but ideally,
                # the calling context (like the service layer) should handle the async nature.
                # For this specific structure, we'll assume it might be called from a sync context
                # that needs to run async code.
                # A more robust solution might involve making translate_batch async throughout the call stack.
                
                # This part is tricky as translate_batch is sync. Ideally, it should be async.
                # Given the current structure, we'll run a new event loop if none is running.
                # If one is running (like in FastAPI), this approach is problematic.
                # The `html_translator.py` calls this synchronously.
                # Let's adjust `translate_html` to be async to properly handle this.
                # For now, let's proceed with a temporary solution for this sync method.
                # A proper fix would involve making the call stack async.

                # Quick fix: Use asyncio.run() if no loop is running.
                # This is not ideal if called from within an already running asyncio loop.
                # A better approach is to make the `translate_batch` method itself async.
                # Let's assume for now this will be handled by an async caller or we adjust the caller.
                # Making this method async directly.
                raise NotImplementedError("This method should be async. The calling stack needs adjustment.")

            else:
                return loop.run_until_complete(translate_all())


        except RuntimeError as e:
             # This handles " asyncio.run() cannot be called from a running event loop"
             # This is a fallback for when called from FastAPI's sync execution path.
             # This is not the most performant way.
             # Ideally, the entire call chain to translate_batch should be async.
            if "cannot be called from a running event loop" in str(e):
                # If we are in a running loop (e.g. FastAPI), we cannot call asyncio.run()
                # A common pattern is to use `asyncio.create_task` if this were an async function
                # or use a thread pool executor to run the async code and block for its result.
                # For now, we'll raise an error indicating this structural issue.
                # print("Warning: Running OpenAI translation synchronously within an event loop. This is not ideal.")
                # This indicates a deeper refactoring might be needed if performance is critical.
                # A simple but less performant way in sync context:
                # tasks = [self._translate_single_text(text, target_lang, source_lang) for text in texts]
                # results = []
                # for task_coro in tasks:
                #     results.append(asyncio.ensure_future(task_coro)) # This won't work as expected without await
                # This is a structural issue with calling async code from a sync method in an async environment.
                # The best solution is to make translate_batch async.
                # Let's assume for now that the calling code will be adapted or this provider is used in a context
                # where a new loop can be started.
                # Given the constraints, this will be a placeholder or require restructuring.
                
                # Let's make `translate_batch` async
                raise NotImplementedError("OpenAITranslationProvider.translate_batch should be async. Please refactor the call stack.")
            raise e

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
                    # Log or handle specific exceptions
                    logger.error(f"Error translating text item {i}: {texts[i]} -> {res}")
                    # Raise a general error or return a placeholder for this item
                    raise HTTPException(status_code=502, detail=f"Error translating item: {texts[i]}") from res
                results.append(res)
            return results
            
        except Exception as e:
            # This catches errors from asyncio.gather itself or other unexpected errors
            logger.exception(f"OpenAI batch translation error: {e}")
            raise HTTPException(status_code=502, detail=f"OpenAI batch API error: {str(e)}") 