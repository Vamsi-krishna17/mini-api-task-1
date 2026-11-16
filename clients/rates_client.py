
import httpx

from config import settings
from exceptions import CountryNotFoundError, ExternalAPIError


class RatesClient:
    """Adapter for the Frankfurter exchange-rate API."""

    def __init__(self):
        self.base_url = settings.frankfurter_api
        self.timeout = settings.timeout

    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> float:
        """Fetch the exchange rate between two currencies."""

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        url = (
            f"{self.base_url}/rate/"
            f"{from_currency}/{to_currency}"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)

            response.raise_for_status()
            result = response.json()

            # Validate the API response structure.
            if not isinstance(result, dict):
                raise ExternalAPIError(
                    "Frankfurter returned an invalid response."
                )

            rate = result.get("rate")

            # Validate the exchange rate.
            if (
                not isinstance(rate, (int, float))
                or isinstance(rate, bool)
                or rate <= 0
            ):
                raise ExternalAPIError(
                    "Exchange rate is currently unavailable."
                )

            return float(rate)

        except (CountryNotFoundError, ExternalAPIError):
            raise

        except httpx.TimeoutException as exc:
            raise ExternalAPIError(
                "External API request timed out. Please try again."
            ) from exc

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (400, 404, 422):
                raise CountryNotFoundError(
                    "Requested information was not found."
                ) from exc

            raise ExternalAPIError(
                "External API is currently unavailable."
            ) from exc

        except (httpx.RequestError, ValueError) as exc:
            raise ExternalAPIError(
                "Could not connect to the external API or read its response."
            ) from exc
