"""HTML translation service."""
from typing import Iterable
from fastapi import UploadFile

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString

from providers import get_translation_provider
from providers.openai import OpenAITranslationProvider
from .exceptions import FileDecodingError, EmptyFileError, FileProcessingError

# HTML tags to skip during translation
SKIP_TAGS = {
    "script",
    "style",
    "code",
    "pre",
    "noscript",
    "textarea",
    "svg",
    "template",
}


async def get_html_from_upload_file(html_file: UploadFile) -> str:
    """Reads an UploadFile, decodes its content, and returns it as a string.
    
    Args:
        html_file: The UploadFile object representing the uploaded HTML file.
        
    Returns:
        The decoded HTML content as a string.
        
    Raises:
        FileDecodingError: If the file cannot be decoded.
        EmptyFileError: If the file is empty or contains only whitespace.
        FileProcessingError: For other file processing issues.
    """
    try:
        html_content_bytes = await html_file.read()
        try:
            html_content_str = html_content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                html_content_str = html_content_bytes.decode('latin-1')
            except UnicodeDecodeError as ude:
                raise FileDecodingError(original_exception=ude) from ude

        if not html_content_str.strip():
            raise EmptyFileError()
        
        return html_content_str
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"An unexpected error occurred while processing the file: {e}") from e
    finally:
        if hasattr(html_file, 'close'):
            await html_file.close()


def _iter_nodes(soup: BeautifulSoup) -> Iterable[NavigableString]:
    """Iterate through text nodes in HTML that should be translated.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Yields:
        Text nodes that should be translated
    """
    for node in soup.find_all(string=True):
        if (
            isinstance(node, (Comment, Doctype))
            or not node.strip()
            or node.parent.name in SKIP_TAGS
        ):
            continue
        yield node


async def translate_html(
    html: str,
    target_lang: str,
    source_lang: str | None = None,
    batch_size: int = 100,
) -> str:
    """Translate HTML content while preserving structure.
    
    Args:
        html: Raw HTML string to translate
        target_lang: BCP-47 language code for target language
        source_lang: Optional BCP-47 language code for source language
        batch_size: Maximum number of strings to translate in one batch
        
    Returns:
        Translated HTML as string
    """
    soup = BeautifulSoup(html, "html.parser")
    nodes = list(_iter_nodes(soup))
    
    # No text to translate
    if not nodes:
        return html
        
    # Get the configured translation provider
    translator = get_translation_provider()
    
    # Process nodes in batches
    for i in range(0, len(nodes), batch_size):
        chunk = nodes[i:i + batch_size]
        
        # Use the async method if the provider supports it
        if hasattr(translator, 'translate_batch_async'):
            translations = await translator.translate_batch_async(
                [n.string for n in chunk], 
                target_lang, 
                source_lang
            )
        else: # Fallback to sync method for other providers
            translations = translator.translate_batch(
                [n.string for n in chunk], 
                target_lang, 
                source_lang
            )
        
        # Replace original text with translations
        for node, translation in zip(chunk, translations):
            node.replace_with(NavigableString(translation))
            
    return str(soup) 