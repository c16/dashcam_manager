"""Custom exceptions for dashcam API operations."""


class DashcamAPIError(Exception):
    """Base exception for dashcam API errors."""
    pass


class ConnectionError(DashcamAPIError):
    """Raised when unable to connect to dashcam."""
    pass


class AuthenticationError(DashcamAPIError):
    """Raised when client registration fails."""
    pass


class FileNotFoundError(DashcamAPIError):
    """Raised when requested file doesn't exist on dashcam."""
    pass


class DownloadError(DashcamAPIError):
    """Raised when file download fails."""
    pass


class UnsupportedOperationError(DashcamAPIError):
    """Raised when dashcam doesn't support requested operation."""
    pass
