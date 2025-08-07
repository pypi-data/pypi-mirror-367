class NotesSDKError(Exception):
    """Base exception class for all errors raised by the Notes SDK."""
    pass

class APIError(NotesSDKError):
    """
    Raised when the API returns an error response (e.g., 4xx or 5xx).
    This indicates a problem with the request or a server-side issue.
    """
    pass

class AuthenticationError(NotesSDKError):
    """
    Raised specifically for 401 Unauthorized errors.
    This indicates that the provided API key is invalid or missing.
    """
    pass

