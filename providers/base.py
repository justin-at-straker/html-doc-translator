"""Base translation provider interface."""
from abc import ABC, abstractmethod
from typing import List


class TranslationProvider(ABC):
    """Abstract base class for translation providers."""

    @abstractmethod
    def translate_batch(
        self, texts: List[str], target_lang: str, source_lang: str | None = None
    ) -> List[str]:
        """Translate a batch of strings from source language to target language.
        
        Args:
            texts: List of text strings to translate
            target_lang: BCP-47 language code for target language
            source_lang: Optional BCP-47 language code for source language
            
        Returns:
            List of translated strings in the same order as input
        """
        pass 