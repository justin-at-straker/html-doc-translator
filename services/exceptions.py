"""Custom exceptions for the service layer."""

class ServiceException(Exception):
    """Base class for service layer exceptions."""
    pass

class FileProcessingError(ServiceException):
    """Base class for file processing errors."""
    pass

class FileDecodingError(FileProcessingError):
    """Raised when a file cannot be decoded."""
    def __init__(self, original_exception: Exception | None = None):
        self.original_exception = original_exception
        super().__init__(f"Could not decode HTML file. Ensure it is UTF-8 or Latin-1 encoded. Error: {original_exception}")

class EmptyFileError(FileProcessingError):
    """Raised when an uploaded file is empty or contains only whitespace."""
    def __init__(self):
        super().__init__("Uploaded HTML file is empty or contains only whitespace.")

class TranslationError(ServiceException):
    """Base class for errors that occur during the translation process itself."""
    pass

class TranslationAPIError(TranslationError):
    """Raised when a translation provider's API call fails."""
    def __init__(self, provider_name: str, original_exception: Exception | None = None, detail: str | None = None):
        self.provider_name = provider_name
        self.original_exception = original_exception
        message = f"Error with {provider_name} Translation API" 
        if detail: 
            message += f": {detail}"
        elif original_exception:
            message += f": {str(original_exception)}"
        super().__init__(message)

class InsufficientQuotaError(TranslationAPIError):
    """Raised when a translation provider reports an insufficient quota."""
    def __init__(self, provider_name: str, original_exception: Exception | None = None):
        super().__init__(
            provider_name=provider_name, 
            original_exception=original_exception,
            detail="The translation API quota has been exceeded."
        ) 