class DriverError(Exception):
    """Base class for driver-specific errors."""


class ConnectionFailed(DriverError):
    """A Connection error occurred."""


class Timeout(DriverError):
    """The request timed out."""
