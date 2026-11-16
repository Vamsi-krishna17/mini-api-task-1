
class CountryNotFoundError(Exception):
    """Raised when requested country information cannot be found."""
    pass


class ExternalAPIError(Exception):
    """Raised when an external API fails or times out."""
    pass
