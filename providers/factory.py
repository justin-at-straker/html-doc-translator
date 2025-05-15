"""Translation provider factory to support different translation services."""
from functools import lru_cache

from config import get_settings
from providers.base import TranslationProvider
from providers.google import GoogleTranslationProvider
from providers.openai import OpenAITranslationProvider
from .dummy import DummyTranslationProvider


@lru_cache(maxsize=1)
def get_translation_provider() -> TranslationProvider:
    """Factory function to get the configured translation provider.
    
    Returns:
        Instance of the configured TranslationProvider
        
    Raises:
        ValueError: If the requested provider is not supported
    """
    settings = get_settings()
    
    if settings.translation_provider.lower() == "google":
        return GoogleTranslationProvider()
    elif settings.translation_provider.lower() == "openai":
        return OpenAITranslationProvider()
    elif settings.translation_provider.lower() == "dummy":
        return DummyTranslationProvider()
        
    # Add additional provider implementations here
    # elif settings.translation_provider.lower() == "azure":
    #     return AzureTranslationProvider()
    # elif settings.translation_provider.lower() == "aws":
    #     return AwsTranslationProvider()
        
    raise ValueError(f"Unsupported translation provider: {settings.translation_provider}") 