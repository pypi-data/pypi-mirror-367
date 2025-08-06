"""Custom exceptions for raxodus."""


class RaxodusError(Exception):
    """Base exception for raxodus."""
    pass


class AuthenticationError(RaxodusError):
    """Authentication failed."""
    pass


class RateLimitError(RaxodusError):
    """Rate limited by API."""
    pass


class ConfigError(RaxodusError):
    """Configuration error."""
    pass
