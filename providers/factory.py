"""Translation provider factory to support different translation services."""
from functools import lru_cache
from typing import List, Type # Import Type for type hinting provider classes

from config import get_settings
from providers.base import TranslationProvider
from providers.google import GoogleTranslationProvider
from providers.openai import OpenAITranslationProvider
from .dummy import DummyTranslationProvider

# Define a mapping of provider keys to their classes
AVAILABLE_PROVIDERS: dict[str, Type[TranslationProvider]] = {
    "google": GoogleTranslationProvider,
    "openai": OpenAITranslationProvider,
    "dummy": DummyTranslationProvider,
    # Add new providers here
}

def get_available_provider_names() -> List[str]:
    """Returns a list of keys for available translation providers."""
    return list(AVAILABLE_PROVIDERS.keys())

@lru_cache(maxsize=1)
def get_translation_provider() -> TranslationProvider:
    """Factory function to get the configured translation provider.
    
    Returns:
        Instance of the configured TranslationProvider
        
    Raises:
        ValueError: If the requested provider is not supported
    """
    settings = get_settings()
    provider_key = settings.translation_provider.lower()
    
    if provider_key in AVAILABLE_PROVIDERS:
        ProviderClass = AVAILABLE_PROVIDERS[provider_key]
        return ProviderClass()
        
    raise ValueError(f"Unsupported translation provider: {settings.translation_provider}") 