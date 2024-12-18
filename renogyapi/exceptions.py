"""Provide exceptions for renogyapi."""


class UrlNotFound(Exception):
    """Exception for NotFound."""


class NotAuthorized(Exception):
    """Exception for invalid API key."""


class APIError(Exception):
    """Exception for API errors."""


class RateLimit(Exception):
    """Exception for API errors."""


class InvalidCall(Exception):
    """Exception for missing device_id."""


class NoDevices(Exception):
    """Exception for missing device_id."""
