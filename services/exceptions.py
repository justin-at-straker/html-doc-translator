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