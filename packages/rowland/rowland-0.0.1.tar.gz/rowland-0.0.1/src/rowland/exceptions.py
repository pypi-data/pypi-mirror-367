"""Exceptions for the Rowland SDK."""


class RowlandError(Exception):
    """Base exception for Rowland SDK errors."""

    pass


class RowlandHTTPError(RowlandError):
    """HTTP error exception."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_text: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class RowlandAuthenticationError(RowlandHTTPError):
    """Authentication error exception."""

    def __init__(
        self,
        message: str = "Authentication failed",
        response_text: str | None = None,
    ):
        super().__init__(message, 401, response_text)
