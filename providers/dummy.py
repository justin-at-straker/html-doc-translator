"""Dummy Translation provider for testing."""
from typing import List
import asyncio # For async version
import logging # Import logging

from providers.base import TranslationProvider

# Get a logger for this module
logger = logging.getLogger(__name__)

class DummyTranslationProvider(TranslationProvider):
    """A dummy translation provider that returns a modified version of the input text.
    
    Useful for testing the application flow without making actual API calls.
    """

    def __init__(self, prefix: str = "[DUMMY_TRANSLATED]: "):
        """Initialize the dummy provider.
        
        Args:
            prefix: A string to prepend to each translated text.
        """
        self.prefix = prefix
        logger.info("Initialized DummyTranslationProvider.") # Use logger

    def translate_batch(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Simulates translation by prepending a prefix to each text.
        
        Ignores target_lang and source_lang.
        """
        logger.info(f"DummyProvider: Received {len(texts)} texts for pseudo-translation to {target_lang} from {source_lang or 'auto'}.") # Use logger
        return [f"{self.prefix}{text}" for text in texts]

    async def translate_batch_async(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Asynchronously simulates translation by prepending a prefix.
        
        Ignores target_lang and source_lang.
        """
        logger.info(f"DummyProvider (async): Received {len(texts)} texts for pseudo-translation to {target_lang} from {source_lang or 'auto'}.") # Use logger
        # Simulate a small async delay if needed, though not strictly necessary for a dummy
        # await asyncio.sleep(0.01)
        return [f"{self.prefix}{text}" for text in texts] 