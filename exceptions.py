
class NotFoundError(Exception):
    """Base exception for resources that cannot be found."""
    pass


class CountryNotFoundError(NotFoundError):
    """Raised when country information cannot be found."""
    pass


class TripNotFoundError(NotFoundError):
    """Raised when a requested trip does not exist."""
    pass


class ExternalAPIError(Exception):
    """Raised when an external API fails or times out."""
    pass
