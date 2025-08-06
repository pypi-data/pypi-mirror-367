"""
Facebook exceptions
"""


class FacebookError(Exception):
    """
    Base exception for Facebook API errors
    """

    def __init__(self, message: str, error_data: dict | None = None):
        super().__init__(message)
        self.error_data = error_data


class FacebookAPIError(FacebookError):
    """
    Raised when Facebook API returns an error response

    """

    pass


class FacebookValidationError(FacebookError):
    """
    Raised when response validation fails
    """

    pass
